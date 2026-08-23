"""
Database engine and session setup.

Kept minimal and framework-standard: one engine, one sessionmaker, one
`get_db` FastAPI dependency that yields a session and always closes it.
Real infrastructure detail -- domain and application layers never import
from this file directly.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url) if settings.database_url else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()