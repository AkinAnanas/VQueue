from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


"""
Represents the users of a service provided by service provider.
Grouped into batches called Blocks. 
"""
class Party(Base):
    __tablename__ = "parties"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    party_size = Column(Integer) # number of people in the party


"""
Represents an organization that manages 
virtual queues and blocks.
"""
class ServiceProvider(Base):
    __tablename__ = "service_providers"
    id = Column(Integer, primary_key=True)
    name = Column(String)


"""
Represents a batch of parties waiting to use the service 
provided by a ServiceProvider.
Is the building block for a queue.
"""
class Block(Base):
    __tablename__ = "blocks"
    id = Column(Integer, primary_key=True)
    name = Column(String)
