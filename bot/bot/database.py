"""Database session for bot handlers."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from bot.config import settings

# Create engine
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Session:
    """Get a database session."""
    return SessionLocal()
