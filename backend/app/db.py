import os
from redis import Redis
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

pg_conn_string = \
    (f'postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}'
     f'@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}')

redis_conn_string = \
    f'redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}'

engine = create_engine(pg_conn_string, echo=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"DB session error: {e}")
    finally:
        db.close()

def get_redis():
    try:
        rdb = Redis(host="localhost", port=6379, decode_responses=True)
    except Exception as e:
        print(f"Redis connection error: {e}")
        rdb = None
    finally:
        yield rdb