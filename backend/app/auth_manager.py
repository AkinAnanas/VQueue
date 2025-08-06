import phonenumbers
import bcrypt
from random import randint
from redis import Redis

def store_otp(rdb: Redis, phone: str, otp: str, ttl: int = 300):
    rdb.setex(f"otp:{phone}", ttl, hash_otp(otp))

def get_otp(rdb: Redis, phone: str):
    return rdb.get(f"otp:{phone}")

def delete_otp(rdb: Redis, phone: str):
    rdb.delete(f"otp:{phone}")

def normalize(phone: str, region: str = "US") -> str:
    parsed = phonenumbers.parse(phone, region)
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Invalid phone number")
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

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

def create_jwt(phone: str) -> str:
    # Placeholder for JWT creation logic
    return f"token-for-{phone}"

def get_token():
    # Placeholder for token extraction logic from request
    return "extracted-token"