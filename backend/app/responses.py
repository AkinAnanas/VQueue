from pydantic import BaseModel, EmailStr
from app.queues import PartyInfo, QueueInfo
from typing import List, Optional

class Response(BaseModel):
    status_code: int
    body: Optional[dict] = None

class JoinQueueResponse(BaseModel):
    status_code: int
    body: PartyInfo  # or a more specific model like PartyInfo

class QueueStatusResponse(BaseModel):
    status_code: int
    body: dict  # e.g. {"block_count": 3, "estimated_wait": "10 min"}

class QueueInfoResponse(BaseModel):
    status_code: int
    body: QueueInfo

class QueueListResponse(BaseModel):
    status_code: int
    total: int
    body: List[QueueInfo]
    limit: Optional[int] = None
    offset: Optional[int] = None
