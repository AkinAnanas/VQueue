import logging
from fastapi import APIRouter, HTTPException
from app.auth.manager import send_sms, generate_otp, store_otp, get_otp, verify_otp, delete_otp
from app.auth.manager import create_tokens, get_token, parse_token, verify_password, hash_password
from app.utils import normalize_phone, normalize_email, sanitize_str
from redis import Redis
from fastapi import Depends, Body
from fastapi.security import HTTPBearer
from app.db import get_db, get_redis
from app.models import Party, ServiceProvider
from app.responses import Response
from app.identities import PartyInfo, ServiceProviderInfo, LoginRequest
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth")
security = HTTPBearer()

"""
Auth
"""
@router.post("/login")
def login(payload: PartyInfo, rdb: Redis = Depends(get_redis)):
    try:
        phone = normalize_phone(payload.phone)
        otp = generate_otp()
        store_otp(rdb, phone, otp)
        send_sms(phone, otp)  # Twilio
        return Response(status_code=200, body={"message": "OTP sent"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify")
def verify(payload: PartyInfo, rdb: Redis = Depends(get_redis), db: Session = Depends(get_db)):
    if not payload.otp:
        return Response(status_code=400, body={"error": "Missing OTP"})
    phone = normalize_phone(payload.phone)
    submitted_otp = payload.otp
    stored_otp = get_otp(rdb, phone)
    if not stored_otp or not verify_otp(submitted_otp, stored_otp):
        return Response(status_code=401, body={"error": "Invalid OTP"})
    delete_otp(rdb, phone)
    access_token, refresh_token = create_tokens(phone, rdb)

    # Create the user in the DB if not exists
    db_party = db.get(Party, phone)
    if not db_party:
        new_party = Party(
            phone=payload.phone, 
            name=payload.name, 
            size=payload.party_size, 
            priority=payload.priority,
            last_login=datetime.now(timezone.utc)
        )
        db.add(new_party)
        db.commit()
    else:
        db_party.last_login = datetime.now(timezone.utc)
        db.commit()

    return Response(status_code=200, body={"access_token": access_token})

@router.post("/logout", dependencies=[Depends(security)])
def logout(token: str = Depends(get_token), rdb: Redis = Depends(get_redis)):
    token_data = parse_token(token)
    id = token_data["sub"]
    rdb.setex(f"blacklist:{token}", timedelta(hours=1), "revoked")
    refresh_token = rdb.get(f"refresh_by_id:{id}")
    if refresh_token:
        rdb.delete(f"refresh:{refresh_token}")
        rdb.delete(f"refresh_by_id:{id}")
    return Response(status_code=200, body={"message": "Logged out successfully"})

@router.post("/auth/refresh")
def refresh_token(refresh_token: str = Body(...), rdb: Redis = Depends(get_redis)):
    id = rdb.get(f"refresh:{refresh_token}")
    if not id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    rdb.delete(f"refresh:{refresh_token}")
    rdb.delete(f"refresh_by_id:{id}")
    access_token, new_refresh = create_tokens(id.decode(), rdb)
    rdb.setex(f"refresh:{new_refresh}", timedelta(days=7), id)
    rdb.setex(f"refresh_by_id:{id}", timedelta(days=7), new_refresh)
    return {
        "access_token": access_token,
        "refresh_token": new_refresh
    }

@router.post("/provider/login")
def provider_login(payload: LoginRequest, rdb: Redis = Depends(get_redis), db: Session = Depends(get_db)):
    db_provider = db.query(ServiceProvider).filter(ServiceProvider.email == payload.email).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Email not registered")
    if not verify_password(payload.password, db_provider.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    access_token, refresh_token = create_tokens(str(db_provider.id), rdb)
    db_provider.last_login = datetime.now(timezone.utc)
    db.commit()
    return Response(status_code=200, body={"access_token": access_token, "refresh_token": refresh_token })

@router.post("/provider/register")
def provider_register(payload: ServiceProviderInfo, db: Session = Depends(get_db)):
    try:
        email = normalize_email(payload.email)
        location = sanitize_str(payload.location)
        name = sanitize_str(payload.name)
        existing_provider = db.query(ServiceProvider).filter(ServiceProvider.email == email).first()
        if existing_provider:
            raise HTTPException(status_code=409, detail="Email already registered")
        hashed_pw = hash_password(payload.password)
        new_provider = ServiceProvider(
            name=name,
            email=email,
            hashed_password=hashed_pw,
            location=location,
        )
        db.add(new_provider)
        db.commit()
        return Response(status_code=201, body={"message": "Service provider registered successfully"})
    except Exception as e:
        return Response(status_code=500, body={"error": str(e)})
    
@router.post("/provider/logout", dependencies=[Depends(security)])
def provider_logout(token: str = Depends(get_token), rdb: Redis = Depends(get_redis)):
    token_data = parse_token(token)
    id = token_data["sub"]
    rdb.setex(f"blacklist:{token}", timedelta(hours=1), "revoked")
    refresh_token = rdb.get(f"refresh_by_id:{id}")
    if refresh_token:
        rdb.delete(f"refresh:{refresh_token}")
        rdb.delete(f"refresh_by_id:{id}")
    else: raise HTTPException(status_code=400, detail="No active session found, id={id}")
    return Response(status_code=200, body={"message": "Service provider logged out successfully"})