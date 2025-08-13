import uuid
from typing import Optional
from pydantic import BaseModel
from pydantic_redis import Model
from app.identities import PartyInfo
    
class BlockInfo(BaseModel):
    block_id: str
    parties: list[PartyInfo] = []
    capacity: int = 10  # max number of people in the block

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

class BlockInfoRedis(Model):
    __model__ = BlockInfo
    __key_prefix__ = "block"

class QueueInfo(BaseModel):
    code: Optional[str] = None  # 6-digit alphanumeric code
    service_provider_id: Optional[int] = None
    is_open: Optional[bool] = True
    max_block_capacity: Optional[int] = 100  # max number of people per block per queue, -1 for single file
    max_party_capacity: Optional[int] = 10 # max number of people per party per queue
    size: Optional[int] = 0  # current number of people in the queue
    wait_time_estimate: Optional[str] = "0 min"  # e.g. "15 min"
    manual_dispatch: Optional[bool] = False  # if True, blocks are dispatched manually
    name: Optional[str] = None  # Name of the queue
    description: Optional[str] = None  # Description of the queue
    image_url: Optional[str] = None  # URL to an image representing the queue

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
class QueueInfoRedis(Model):
    __model__ = QueueInfo
    __key_prefix__ = "queue"

class QueueStatus(BaseModel):
    size: int
    wait_time_estimate: str
    name: str
    description: str
    block_count: int
    image_url: str

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)