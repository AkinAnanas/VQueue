import logging
from fastapi import FastAPI
from fastapi import Path, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from sqlalchemy.orm import Session
from app.responses import Response, JoinQueueResponse, QueueStatusResponse
from app.queues import QueueInfo, BlockInfo
from app.identities import PartyInfo, ServiceProviderInfo
from app.utils import generate_code
import app.queue_manager as queue_manager
from app.auth.manager import generate_otp, store_otp, get_otp, verify_otp, delete_otp
from app.auth.manager import send_sms, create_tokens, get_token
from app.models import ServiceProvider, Party
from datetime import timedelta, datetime

from app.db import get_db, get_redis
from app.models import Party

from app.auth.routes import router as auth_router
from app.user.routes import router as user_router
from app.admin.routes import router as admin_router


app = FastAPI()

logging.info("✅ FastAPI app loaded")

# Add this before including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify a list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)

@app.get("/")
async def root():
    return Response(status_code=200, body={ "message": "Welcome to the Queue Management API" })

