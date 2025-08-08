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
from app.queues import QueueInfo
from app import queue_manager
from app.responses import JoinQueueResponse, QueueStatusResponse, Response
from app.utils import generate_code
from sqlalchemy.orm import Session
from app.auth.manager import get_token, parse_token, hash_password

router = APIRouter()
security = HTTPBearer()

"""
User-facing
"""
@router.post("/queue/join/{code}", response_model=JoinQueueResponse)
async def join_queue(
    code: str = Path(..., pattern="^[A-Z0-9]{6}$"),
    payload: PartyInfo = None,
    token: str = Depends(get_token), 
    rdb: Redis = Depends(get_redis)
):
    if payload is None:
        raise HTTPException(status_code=400, detail="Missing request body")
    try:
        party_id, block_id = queue_manager.add_party_to_block(rdb, code, payload)
        return JoinQueueResponse(status_code=200, body={"party_id": party_id, "block_id": block_id})
    except Exception as e:
        return JoinQueueResponse(status_code=500, body={"error": str(e)})


@router.get("/queue/status/{code}", response_model=QueueStatusResponse)
async def status_queue(
    payload: dict, 
    code: str = Path(..., pattern="^[A-Z0-9]{6}$"),
    token: str = Depends(get_token)
):
    # TODO: Implement status retrieval
    return QueueStatusResponse(status_code=200, body={})



"""
ServiceProvider-facing
"""
@router.post("/queue/create", response_model=Response, dependencies=[Depends(security)])
async def create_queue(
    payload: QueueInfo,
    token: str = Depends(get_token), 
    rdb: Redis = Depends(get_redis),
    db: Session = Depends(get_db)
):
    # Generate 6-digit alpha-numeric code associated with queue
    while rdb.exists(f"queue:{code}"):
        code = generate_code()
    
    # Initialize the queue in Redis
    queue_manager.initialize_queue(rdb, payload)

    # Update service provider's list of queues
    service_provider_id = parse_token(token)["sub"]
    service_provider = db.get(ServiceProvider, service_provider_id)
    if service_provider is None:
        raise HTTPException(status_code=404, detail="Service provider not found")
    service_provider.queues.append(code)
    db.commit()

    return Response(status_code=200, body={"queue_code": code})

@router.patch("/queue/update/{code}", response_model=Response, dependencies=[Depends(security)])
async def update_queue(
    payload: QueueInfo,
    code: str = Path(..., pattern="^[A-Z0-9]{6}$"),
    token: str = Depends(get_token)
):
    # Update the status of the queue (e.g., open/close)
    return Response(status_code=204)

@router.delete("/queue/delete/{code}", response_model=Response, dependencies=[Depends(security)])
async def delete_queue(
    payload: QueueInfo,
    code: str = Path(..., pattern="^[A-Z0-9]{6}$"),
    token: str = Depends(get_token), 
    rdb: Redis = Depends(get_redis)
):
    # TODO: Add auth to ensure only service provider can delete
    # Delete the queue and all associated data
    rdb.delete(f"queue:{payload.code}")
    return Response(status_code=200, body={})

@router.post("/queue/dispatch", response_model=Response, dependencies=[Depends(security)])
async def dispatch_queue(
    payload: QueueInfo,
    code: str = Path(..., pattern="^[A-Z0-9]{6}$"),
    token: str = Depends(get_token), 
    rdb: Redis = Depends(get_redis)
):
    # Dispatch the current block in the queue
    return Response(status_code=204)

@router.get("/provider/{id}", response_model=ServiceProviderInfo, dependencies=[Depends(security)])
async def get_service_provider(
    id: int, 
    token: str = Depends(get_token), 
    db: Session = Depends(get_db)
):
    return Response(status_code=200, body=db.get(ServiceProvider, id))

@router.post("/provider/delete/{id}", response_model=Response, dependencies=[Depends(security)])
async def delete_service_provider(
    id: int, 
    token: str = Depends(get_token), 
    db: Session = Depends(get_db)
):
    token_data = parse_token(token)
    if token_data["sub"] != str(id):
        raise HTTPException(status_code=403, detail="Forbidden: Cannot delete other service providers")
    db.delete(db.get(ServiceProvider, id))
    db.commit()
    return Response(status_code=204)

@router.patch("/provider/update/{id}", response_model=Response, dependencies=[Depends(security)])
async def update_service_provider(
    id: int, 
    payload: ServiceProviderInfo,
    token: str = Depends(get_token), 
    db: Session = Depends(get_db)
):
    token_data = parse_token(token)
    if token_data["sub"] != str(id):
        raise HTTPException(status_code=403, detail="Forbidden: Cannot update other service providers")
    service_provider = db.get(ServiceProvider, id)
    # TODO: Validate payload fields
    for key, value in payload.to_dict().items():
        if key != "hashed_password" and value is not None:
            setattr(service_provider, key, value)
        elif key == "hashed_password" and value is not None:
            setattr(service_provider, key, hash_password(value))
    db.commit()
    return Response(status_code=204)
