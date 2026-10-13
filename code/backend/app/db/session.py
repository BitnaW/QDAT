"""DATABASE SESSION MANAGEMENT AND CONNECTION SETUP."""
import os
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://qdat_user:qdat_password@localhost:5432/qdat_db",
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FASTAPI DEPENDENCY FOR YIELDING DATABASE SESSIONS."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
