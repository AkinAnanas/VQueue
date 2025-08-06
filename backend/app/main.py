from fastapi import FastAPI
from fastapi import Path, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import Response, JoinQueueRequest, JoinQueueResponse, QueueStatusResponse, EmptyResponse
from utils import generate_code

from models import Party

app = FastAPI()

@app.get("/")
async def root():
    return Response(200, {})

"""
User-facing
"""
@app.post("/queue/join/{code}", response_model=JoinQueueResponse)
async def join_queue(
    code: str = Path(..., pattern="^[A-Z0-9]{6}$"),
    payload: JoinQueueRequest = None,
    db: Session = Depends(get_db)
):
    if payload is None:
        raise HTTPException(status_code=400, detail="Missing request body")

    try:
        party = Party(name=payload.name, party_size=payload.party_size)
        db.add(party)
        db.commit()
        db.refresh(party)
        return JoinQueueResponse(status_code=200, body={"party_id": party.id})
    except Exception as e:
        db.rollback()
        return JoinQueueResponse(status_code=500, body={"error": str(e)})


@app.get("/queue/status/{code}/{party_id}", response_model=QueueStatusResponse)
async def status_queue(party_id: int, code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    return QueueStatusResponse(200, {})

@app.delete("/queue/{code}/{party_id}", response_model=Response)
async def delete_queue(party_id: int, code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    return Response(200, {})


"""
ServiceProvider-facing
"""
@app.post("/queue/create", response_model=Response)
async def create_queue():
    code = generate_code() # 6-digit alpha-numeric code associated with queue
    return Response(200, {})

@app.patch("/queue/{code}/close", response_model=EmptyResponse)
async def close_queue(code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    # Close the queue
    return EmptyResponse(204)

@app.post("/queue/{code}/dispatch", response_model=EmptyResponse)
async def dispatch_queue(code: str = Path(..., pattern="^[A-Z0-9]{6}$")):
    # Dispatch the current block in the queue
    return EmptyResponse(204)

"""
Dev-facing
"""
@app.get("/dashboard/stats")
async def dashboard_stats():
    return Response(200, {})
