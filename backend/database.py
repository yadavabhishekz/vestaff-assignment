from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from backend.config import SQLITE_URL
from backend.models import base

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},  
    echo=False
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db() -> None:
    base.metadata.create_all(bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

