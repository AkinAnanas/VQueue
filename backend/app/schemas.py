from pydantic import BaseModel
from app.queue_models import PartyInfo
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
