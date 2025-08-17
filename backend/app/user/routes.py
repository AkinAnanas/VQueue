import json
from fastapi import APIRouter, Path, HTTPException
from fastapi.security import HTTPBearer
from redis import Redis
from fastapi import Depends, Query
from fastapi.security import HTTPBearer
from app.db import get_db, get_redis
from app.models import Party, ServiceProvider
from app.responses import Response
from app.identities import PartyInfo, ServiceProviderInfo
from app.queues import QueueInfo
from app import queue_manager
from app.responses import JoinQueueResponse, QueueStatusResponse, Response
from app.responses import QueueInfoResponse, QueueListResponse
from app.utils import generate_code, sanitize_str
from sqlalchemy.orm import Session
from app.auth.manager import get_token, parse_token, hash_password
from typing import Optional

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
    # Get the service provider
    service_provider_id = int(parse_token(token)["sub"])
    service_provider = db.get(ServiceProvider, service_provider_id)
    if service_provider is None:
        raise HTTPException(status_code=404, detail="Service provider not found")
    
    # Generate 6-digit alpha-numeric code associated with queue
    payload.code = generate_code()
    while rdb.exists(f"queue:{payload.code}"):
        payload.code = generate_code()
        
    # Initialize the queue in Redis
    payload.service_provider_id = service_provider_id
    queue_manager.initialize_queue(rdb, payload)

    # Add the queue code to the service provider's list of queues
    service_provider.queue_codes.append(payload.code)
    db.commit()

    return Response(status_code=200, body={"queue_code": payload.code})

@router.get("/queue/{code}", response_model=QueueInfoResponse)
async def get_queue(
    code: str = Path(..., pattern="^[A-Z0-9]{6}$"),
    token: str = Depends(get_token),
    rdb: Redis = Depends(get_redis)
):
    # Ensure queue exists before attempting to delete
    if not rdb.exists(f"queue:{code}"):
        raise HTTPException(status_code=404, detail="Queue not found")
    # Ensure only service provider who owns queue can get it
    id = rdb.get(f"queue:{code}:service_provider_id")
    token_data = parse_token(token)
    if token_data["sub"] != str(id):
        raise HTTPException(status_code=403, detail="Forbidden: Cannot get other service provider queues")
    # Retrieve current queue info
    queue_key = f"queue:{code}"
    raw_data = rdb.lindex(queue_key, 0)
    if not raw_data:
        raise HTTPException(status_code=404, detail="Queue not found")
    parsed_data = QueueInfo.from_dict(json.loads(raw_data))
    return QueueInfoResponse(status_code=200, body=parsed_data)

@router.get("/queues", response_model=QueueListResponse)
async def get_queues(
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token: str = Depends(get_token),
    rdb: Redis = Depends(get_redis),
    db: Session = Depends(get_db)
):
    token_data = parse_token(token)
    service_provider_id = int(token_data["sub"])

    # Get the service provider queues
    sp = db.get(ServiceProvider, service_provider_id)
    if not sp:
        raise HTTPException(status_code=404, detail="Service provider not found")
    queue_codes = sp.queue_codes or []

    matched_queues = []

    # Get queue data and owners
    pipe = rdb.pipeline()
    for code in queue_codes:
        pipe.lindex(f"queue:{code}", 0)
        pipe.get(f"queue:{code}:service_provider_id")
    results = pipe.execute()

    for i in range(0, len(results), 2):
        raw_data, owner_id = results[i], results[i+1]
        if not raw_data:
            continue
        try:
            queue_data = json.loads(raw_data)
        except json.JSONDecodeError:
            continue
        # Check ownership
        if str(owner_id) != str(service_provider_id):
            continue
        # Apply search filter
        if search:
            normalized_search = sanitize_str(search).lower()
            normalized_blob = sanitize_str(raw_data).lower()
            if normalized_search not in normalized_blob:
                continue
        matched_queues.append(QueueInfo.from_dict(queue_data))

    matched_queues.sort(key=lambda q: q.name.lower())
    paginated = matched_queues[offset:offset + limit]
    return QueueListResponse(
        status_code=200, 
        body=paginated,
        total=len(matched_queues),
        limit=limit,
        offset=offset
    )

@router.patch("/queue/update/{code}", response_model=Response, dependencies=[Depends(security)])
async def update_queue(
    payload: QueueInfo,
    code: str = Path(..., pattern="^[A-Z0-9]{6}$"),
    token: str = Depends(get_token),
    rdb: Redis = Depends(get_redis)
):
    # Ensure queue exists before attempting to delete
    if not rdb.exists(f"queue:{code}"):
        raise HTTPException(status_code=404, detail="Queue not found")
    # Ensure only service provider who owns queue can update it
    id = rdb.get(f"queue:{code}:service_provider_id")
    token_data = parse_token(token)
    if token_data["sub"] != str(id):
        raise HTTPException(status_code=403, detail="Forbidden: Cannot update other service provider queues")
    # Retrieve current queue info
    queue_key = f"queue:{code}"
    raw_data = rdb.lindex(queue_key, 0)
    if not raw_data:
        raise HTTPException(status_code=404, detail="Queue not found")
    current_data = json.loads(raw_data)
    # Merge with incoming payload
    updated_data = current_data.copy()
    for key, value in payload.to_dict().items():
        if value is not None:
            if key == "capacity" and value != current_data.get("capacity"):
                raise HTTPException(
                    status_code=400,
                    detail="Cannot update 'capacity'. Create a new queue instead."
                )
            updated_data[key] = value
    # Overwrite Redis entry
    rdb.lset(queue_key, 0, json.dumps(updated_data))
    return Response(status_code=204)


@router.delete("/queue/delete/{code}", response_model=Response, dependencies=[Depends(security)])
async def delete_queue(
    payload: QueueInfo,
    code: str = Path(..., pattern="^[A-Z0-9]{6}$"),
    token: str = Depends(get_token), 
    rdb: Redis = Depends(get_redis),
    db: Session = Depends(get_db)
):
    # Ensure queue exists before attempting to delete
    if not rdb.exists(f"queue:{code}"):
        raise HTTPException(status_code=404, detail="Queue not found")
    # Add auth to ensure only service provider who owns queue can delete it
    id = rdb.get(f"queue:{code}:service_provider_id")
    token_data = parse_token(token)
    if token_data["sub"] != str(id):
        raise HTTPException(status_code=403, detail="Forbidden: Cannot delete other service provider queues")
    # Remove the code from the service provider's list of queues
    sp = db.get(ServiceProvider, id)
    if not sp:
        raise HTTPException(status_code=404, detail="Service provider not found")
    sp.queue_codes.remove(code)
    # Delete the queue and all associated data
    pipe = rdb.pipeline()
    pipe.delete(f"queue:{code}:service_provider_id")
    pipe.delete(f"queue:{code}:block_counter")
    pipe.delete(f"queue:{code}:block_capacity")
    pipe.delete(f"queue:{code}")
    pipe.delete(f"blocks:{code}")
    pipe.execute()
    return Response(status_code=204)

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
    try:
        service_provider = db.get(ServiceProvider, id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"ServiceProvider {id} does not exist")
    return Response(status_code=200, body=service_provider)

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
