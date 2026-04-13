"""
Main application entry point for the Jira Clone API.

This file initializes the FastAPI application, sets up database connections,
includes API routers, and creates database tables.
"""

from fastapi import FastAPI

# Import database components for initialization
from app.db.database import engine
from app.db.base import Base

# Import models to ensure they're registered with SQLAlchemy
from app.models import user
from app.models import organization

# Import API routers
from app.api import user
from app.api import auth
from app.api import organization

# Create the FastAPI application instance
app = FastAPI()

# Include the user management router
app.include_router(user.router)

# Include the authentication router
app.include_router(auth.router)

# Include the organization router for organization and membership endpoints
app.include_router(organization.router)

# Create all database tables defined in the models
# This is done here for development; in production, use migrations
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    """
    Root endpoint that returns a welcome message.

    This is a simple health check endpoint to verify the API is running.
    """
    return {"message": "Jira Clone Backend Running 🚀"}