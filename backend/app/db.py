import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

pg_conn_string = \
    (f'postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}'
     f'@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}')

redis_conn_string = \
    f'redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}'

engine = create_engine(pg_conn_string, echo=True)

connection = engine.connect()
print("Connected to PostgreSQL successfully!")
# ... perform operations ...
connection.close()