import phonenumbers
import logging
import secrets
import bcrypt
import jwt
import os
from dotenv import load_dotenv
from random import randint
from redis import Redis
from app.db import get_redis
from datetime import datetime, timedelta, timezone
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

def store_otp(rdb: Redis, phone: str, otp: str, ttl: int = 300):
    rdb.setex(f"otp:{phone}", ttl, hash_otp(otp))

def get_otp(rdb: Redis, phone: str):
    return rdb.get(f"otp:{phone}")

def delete_otp(rdb: Redis, phone: str):
    rdb.delete(f"otp:{phone}")

def generate_otp(length: int = 6) -> str:
    range_start = 10**(length-1)
    range_end = (10**length)-1
    return str(randint(range_start, range_end))

def hash_otp(otp: str) -> str:
    return bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()

def verify_otp(submitted: str, hashed: str) -> bool:
    return bcrypt.checkpw(submitted.encode(), hashed.encode())

def send_sms(phone: str, otp: str):
    # Placeholder for SMS sending logic (e.g., Twilio)
    print(f"Sending OTP {otp} to phone {phone}")

# ID can be phone number or service provider ID
def create_tokens(id: str, rdb: Redis) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    payload = {
        "sub": id,
        "exp": expiration,
        "iat": datetime.now(timezone.utc)
    }
    access_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    refresh_token = secrets.token_urlsafe(32)
    rdb.setex(f"refresh:{refresh_token}", timedelta(days=7), id)
    rdb.setex(f"refresh_by_id:{id}", timedelta(days=7), refresh_token)
    return [access_token, refresh_token]

def verify_jwt(rdb: Redis, token: str) -> dict:
    # Check if token is blacklisted
    if rdb.get(f"blacklist:{token}"):
        raise ValueError("Token has been revoked")

    # Decode and verify JWT
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

security = HTTPBearer()

def get_auth_header(authorization: str = Header(..., alias="Authorization")) -> str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    return authorization.replace("Bearer ", "").strip()

def get_token(
    token: str = Depends(get_auth_header),
    rdb: Redis = Depends(get_redis)
) -> str:
    try:
        # This will check blacklist, expiration, and validity
        verify_jwt(rdb, token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return token

def parse_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
