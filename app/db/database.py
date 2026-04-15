"""
Database configuration and connection management.

This module sets up the SQLAlchemy database engine, session factory,
and provides a dependency function for getting database sessions in API endpoints.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL

# Create the SQLAlchemy engine using the database URL from config
# This engine manages the connection pool and database interactions
engine = create_engine(DATABASE_URL)

# Create a session factory that will generate database sessions
# autocommit=False and autoflush=False for better control
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """
    Dependency function that provides a database session.

    This function is used as a FastAPI dependency to inject database sessions
    into API endpoints. It ensures proper session lifecycle management.

    Yields:
        Session: A SQLAlchemy database session

    The session is automatically closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()