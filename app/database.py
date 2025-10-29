import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base   

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")


SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db/{POSTGRES_DB}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

BaseSQL = declarative_base()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
