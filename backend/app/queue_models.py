import uuid
from pydantic import BaseModel
from pydantic import Field
from pydantic_redis import Model

class PartyInfo(BaseModel):
    party_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    party_size: int = 1
    priority: int = 0  # e.g. 0 = normal, 1 = VIP

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
class PartyInfoRedis(Model):
    __model__ = PartyInfo
    __key_prefix__ = "party"
    
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
    code: str  # 6-digit alphanumeric code
    service_provider_id: int
    is_open: bool = True
    capacity: int = 100  # max number of people in the queue
    size: int = 0  # current number of people in the queue
    wait_time_estimate: str = "0 min"  # e.g. "15 min"
    manual_dispatch: bool = False  # if True, blocks are dispatched manually

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
class QueueInfoRedis(Model):
    __model__ = QueueInfo
    __key_prefix__ = "queue"