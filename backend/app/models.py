from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime, Boolean
from datetime import datetime

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
    block_id = Column(Integer)  # Foreign key to Block

    created_at = Column(DateTime, default=datetime.now())
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

"""
Represents an organization that manages 
virtual queues and blocks.
"""
class ServiceProvider(Base):
    __tablename__ = "service_providers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    queue_codes = Column(ARRAY(String))  # List of queue codes

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
    created_at = Column(DateTime, default=datetime.utcnow)
    service_provider_id = Column(Integer) # Foreign key to ServiceProvider
    queue_code = Column(String)  # 6-digit alphanumeric code associated with the block's queue
