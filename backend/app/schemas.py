from pydantic import BaseModel
from typing import List, Optional

class FormatResponse(BaseModel):
    status_code: int
    body: str

class JoinQueueRequest(BaseModel):
    name: str
    party_size: int

class JoinQueueResponse(BaseModel):
    status_code: int
    body: dict  # or a more specific model like PartyInfo

class QueueStatusResponse(BaseModel):
    status_code: int
    body: dict  # e.g. {"block_count": 3, "estimated_wait": "10 min"}
