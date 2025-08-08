from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()


"""
Represents the users of a service provided by service provider.
Grouped into batches called Blocks. 
"""
class Party(Base):
    __tablename__ = "parties"

    phone = Column(String, primary_key=True)  # E.164 format, e.g., "+1234567890"
    name = Column(String)
    size = Column(Integer)
    priority = Column(Integer, default=0)
    block_id = Column(String, ForeignKey("blocks.id"))  # queue:{code}:block_id
    block = relationship("Block", back_populates="parties")

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_login = Column(DateTime)

"""
Represents an organization that manages 
virtual queues and blocks.
"""
class ServiceProvider(Base):
    __tablename__ = "service_providers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    location = Column(String, nullable=True)
    queue_codes = Column(ARRAY(String), nullable=False)  # List of queue codes
    blocks = relationship("Block", back_populates="service_provider")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.queue_codes is None:
            self.queue_codes = []

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_login = Column(DateTime)

"""
Represents a batch of parties waiting to use the service 
provided by a ServiceProvider.
Is the building block for a queue.
"""
class Block(Base):
    __tablename__ = "blocks"
    id = Column(String, primary_key=True)
    capacity = Column(Integer)  # max number of people in the block
    status = Column(String)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    dispatched_at = Column(DateTime)
    service_provider_id = Column(Integer, ForeignKey("service_providers.id"))
    service_provider = relationship("ServiceProvider", back_populates="blocks")
    parties = relationship("Party", back_populates="block")
    queue_code = Column(String)  # 6-digit alphanumeric code associated with the block's queue
