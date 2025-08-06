from fastapi import FastAPI
from fastapi import Path, Depends, HTTPException
from redis import Redis
from sqlalchemy.orm import Session
from app.schemas import Response, JoinQueueResponse, QueueStatusResponse
from app.queue_models import PartyInfo, QueueInfo, BlockInfo
from app.utils import generate_code
import app.queue_manager as queue_manager
from app.auth_manager import generate_otp, store_otp, get_otp, verify_otp, delete_otp
from app.auth_manager import normalize, send_sms, create_jwt, get_token
from app.models import ServiceProvider, Party
from datetime import timedelta

from app.db import get_db, get_redis
from app.models import Party

app = FastAPI()

print("✅ FastAPI app loaded")

@app.get("/")
async def root():
    return Response(status_code=200, body={ "message": "Welcome to the Queue Management API" })

"""
Auth
"""
@app.post("/auth/login")
def login(payload: dict, rdb: Redis = Depends(get_redis)):
    if payload is None:
        return Response(status_code=400, body={"error": "Missing request body"})
    try:
        phone = normalize(payload["phone"])
        otp = generate_otp()
        print(f"Generated OTP for {phone}: {otp}")
        store_otp(rdb, phone, otp)
        send_sms(phone, otp)  # Twilio
        return Response(status_code=200, body={"message": "OTP sent"})
    except Exception as e:
        return Response(status_code=500, body={"error": str(e)})

@app.post("/auth/verify")
def verify(payload: dict, rdb: Redis = Depends(get_redis)):
    if payload is None:
        raise Response(status_code=400, body={"error": "Missing request body"})
    phone = normalize(payload["phone"])
    submitted_otp = payload["otp"]
    stored_otp = get_otp(rdb, phone)
    if not stored_otp or not verify_otp(submitted_otp, stored_otp.decode()):
        raise Response(status_code=401, body={"error": "Invalid OTP"})
    delete_otp(rdb, phone)
    token = create_jwt(phone)
    return Response(status_code=200, body={"access_token": token})

@app.post("/auth/logout")
def logout(token: str = Depends(get_token), rdb: Redis = Depends(get_redis)):
    # Optional: store token in Redis blacklist with expiry
    rdb.setex(f"blacklist:{token}", timedelta(hours=1), "revoked")
    return Response(status_code=200, body={"message": "Logged out"})

"""
User-facing
"""
@app.post("/queue/join/{code}", response_model=JoinQueueResponse)
async def join_queue(
    code: str = Path(..., pattern="^[A-Z0-9]{6}$"),
    payload: PartyInfo = None,
    rdb: Redis = Depends(get_redis)
):
    if payload is None:
        raise HTTPException(status_code=400, detail="Missing request body")
    try:
        party_id, block_id = queue_manager.add_party_to_block(rdb, code, payload)
        return JoinQueueResponse(status_code=200, body={"party_id": party_id, "block_id": block_id})
    except Exception as e:
        return JoinQueueResponse(status_code=500, body={"error": str(e)})


@app.get("/queue/status/{code}/{party_id}", response_model=QueueStatusResponse)
async def status_queue(party_id: int, code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    return QueueStatusResponse(status_code=200, body={})

@app.delete("/queue/{code}/{party_id}", response_model=Response)
async def delete_queue(party_id: int, code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    return Response(status_code=200, body={})


"""
ServiceProvider-facing
"""
@app.post("/queue/create", response_model=Response)
async def create_queue(rdb: Redis = Depends(get_redis)):
    code = generate_code() # 6-digit alpha-numeric code associated with queue
    return Response(status_code=200, body={"queue_code": code})

@app.patch("/queue/{code}/close", response_model=Response)
async def close_queue(code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    # Close the queue
    return Response(status_code=204)

@app.post("/queue/{code}/dispatch", response_model=Response)
async def dispatch_queue(code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    # Dispatch the current block in the queue
    return Response(status_code=204)

@app.get("/service_provider/{id}", response_model=Response)
async def get_service_provider(id: int, db: Session = Depends(get_db)):
    return Response(status_code=200, body=db.get(ServiceProvider, id))

@app.post("/service_provider/create", response_model=Response)
async def create_service_provider(db: Session = Depends(get_db), payload: dict = None):
    db.add(ServiceProvider(name=payload.get("name", None), queue_codes=[]))
    db.commit()
    return Response(status_code=200, body={})

@app.post("/service_provider/delete/{id}", response_model=Response)
async def delete_service_provider(id: int, db: Session = Depends(get_db)):
    db.delete(db.get(ServiceProvider, id))
    db.commit()
    return Response(status_code=204)

"""
Dev-facing
"""
@app.get("/dashboard/stats")
async def dashboard_stats():
    return Response(status_code=200, body={})
