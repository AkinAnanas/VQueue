from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic_redis import Model

class PartyInfo(BaseModel):
    phone: str
    name: str
    party_size: int = 1
    priority: int = 0  # e.g. 0 = normal, 1 = VIP
    otp: Optional[str] = None  # for auth purposes

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
class PartyInfoRedis(Model):
    __model__ = PartyInfo
    __key_prefix__ = "party"

class ServiceProviderInfo(BaseModel):
    provider_id: Optional[int] = None
    name: str
    email: EmailStr
    password: str
    queue_codes: Optional[list[str]] = []
    location: Optional[str] = None

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)