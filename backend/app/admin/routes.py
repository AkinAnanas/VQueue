import logging
from fastapi import APIRouter, Path, HTTPException
from fastapi.security import HTTPBearer
from redis import Redis
from fastapi import Depends, Header, Request
from fastapi.security import HTTPBearer
from app.db import get_db, get_redis
from app.models import Party, ServiceProvider
from app.responses import Response
from app.identities import PartyInfo, ServiceProviderInfo
from app import queue_manager
from app.responses import Response
from app.utils import generate_code
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin")

"""
Dev-facing
"""

@router.get("/providers", response_model=Response)
async def list_service_providers(
    db: Session = Depends(get_db)
):
    try:
        providers = db.query(ServiceProvider).all()
        provider_list = [
            {
                "id": sp.id,
                "name": sp.name,
                "email": sp.email,
                "created_at": sp.created_at,
            }
            for sp in providers
        ]
        return Response(status_code=200, body={"service_providers": provider_list})
    except Exception as e:
        return Response(status_code=500, body={"error": str(e)})

@router.get("/parties", response_model=Response)
async def list_parties(
    db: Session = Depends(get_db)
):
    try:
        parties = db.query(Party).all()
        party_list = [
            {
                "phone": p.phone,
                "name": p.name,
                "size": p.size,
                "priority": p.priority,
                "created_at": p.created_at,
                "last_login": p.last_login,
            }
            for p in parties
        ]
        return Response(status_code=200, body={"parties": party_list})
    except Exception as e:
        return Response(status_code=500, body={"error": str(e)})
    