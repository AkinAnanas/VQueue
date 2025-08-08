import os, logging
from redis import Redis
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(
    level=logging.DEBUG,  # Or INFO for less verbosity
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

load_dotenv()

pg_conn_string = \
    (f'postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}'
     f'@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}')

redis_conn_string = \
    f'redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}'

engine = create_engine(pg_conn_string, echo=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

"""Dependency to get Postgres DB session"""
def get_db():
    db = SessionLocal()
    try:
        logging.info("Connected to PostgreSQL")
        yield db
    except BaseException as e:
        logging.error(f"DB session error: {e}")
        raise e
    finally:
        db.close()

"""Dependency to get Redis client"""
def get_redis():
    rdb = Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=0, decode_responses=True)
    try:
        logging.info("Connected to Redis")
        yield rdb
    except BaseException as e:
        logging.error(f"Redis connection error: {e}")
        raise e
