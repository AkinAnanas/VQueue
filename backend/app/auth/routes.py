import logging
from fastapi import APIRouter
from app.auth.manager import generate_otp, store_otp, get_otp, verify_otp, delete_otp
from app.auth.manager import send_sms, create_jwt, get_token, verify_password, hash_password
from app.utils import normalize_phone, normalize_email, validate_email
from redis import Redis
from fastapi import Depends, Header, Request
from fastapi.security import HTTPBearer
from app.db import get_db, get_redis
from app.models import Party, ServiceProvider
from app.responses import Response
from app.identities import PartyInfo, ServiceProviderInfo
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
        return Response(status_code=500, body={"error": str(e)})

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
    token = create_jwt(phone)

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

    return Response(status_code=200, body={"access_token": token})

@router.post("/logout", dependencies=[Depends(security)])
def logout(token: str = Depends(get_token), rdb: Redis = Depends(get_redis)):
    rdb.setex(f"blacklist:{token}", timedelta(hours=1), "revoked")
    return Response(status_code=200, body={"message": "Logged out successfully"})

@router.post("/provider/login")
def provider_login(payload: ServiceProviderInfo, db: Session = Depends(get_db)):
    try:
        email = payload.email
        db_provider = db.query(ServiceProvider).filter(ServiceProvider.email == email).first()
        if not db_provider:
            return Response(status_code=404, body={"error": "Email not registered"})
        if not verify_password(payload.password, db_provider.hashed_password):
            return Response(status_code=401, body={"error": "Invalid password"})
        token = create_jwt(str(db_provider.id))
        db_provider.last_login = datetime.now(timezone.utc)
        db.commit()
        return Response(status_code=200, body={"access_token": token})
    except Exception as e:
        return Response(status_code=500, body={"error": str(e)})

@router.post("/provider/register")
def provider_register(payload: ServiceProviderInfo, db: Session = Depends(get_db)):
    try:
        email = normalize_email(payload.email)
        existing_provider = db.query(ServiceProvider).filter(ServiceProvider.email == email).first()
        if existing_provider:
            return Response(status_code=409, body={"error": "Email already registered"})
        hashed_pw = hash_password(payload.password)
        new_provider = ServiceProvider(
            name=payload.name,
            email=email,
            hashed_password=hashed_pw,
        )
        db.add(new_provider)
        db.commit()
        return Response(status_code=201, body={"message": "Service provider registered successfully"})
    except Exception as e:
        return Response(status_code=500, body={"error": str(e)})
    
@router.post("/provider/logout", dependencies=[Depends(security)])
def provider_logout(token: str = Depends(get_token), rdb: Redis = Depends(get_redis)):
    rdb.setex(f"blacklist:{token}", timedelta(hours=1), "revoked")
    return Response(status_code=200, body={"message": "Service provider logged out successfully"})