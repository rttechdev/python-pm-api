"""
Authentication API endpoints.

This module defines the API routes for user authentication,
including login functionality with JWT token generation.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token

# Create router for authentication endpoints with prefix and tags
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", summary="User login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token.

    This endpoint verifies user credentials and returns a JWT access token
    for authenticated API access.

    - **email**: User's email address
    - **password**: User's password

    Returns a JWT access token for authenticated requests.

    Raises:
        HTTPException: If credentials are invalid (401 status)
    """
    # Query the database for a user with the provided email
    user = db.query(User).filter(User.email == email).first()

    # Check if user exists and password is correct
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate JWT access token with user ID
    token = create_access_token({"user_id": user.id})

    # Return the access token
    return {"access_token": token}