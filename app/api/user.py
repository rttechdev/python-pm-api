"""
User management API endpoints.

This module defines the API routes for user-related operations,
including user registration and management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse

from app.core.security import hash_password

# Create router for user endpoints with Swagger tags
router = APIRouter(tags=["Users"])

@router.post("/users", response_model=UserResponse, summary="Create a new user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    This endpoint allows registration of new users. It validates the input data,
    hashes the password securely, and stores the user in the database.

    - **name**: User's full name
    - **email**: User's email address (must be unique)
    - **password**: User's password (will be hashed before storage)

    Returns the created user with id, name, and email.

    Raises:
        HTTPException: If email is already registered (400 status)
    """
    # Create a new User model instance with hashed password
    db_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)  # Hash password for security
    )

    try:
        # Add user to database session
        db.add(db_user)
        # Commit the transaction to save to database
        db.commit()
        # Refresh to get the auto-generated ID
        db.refresh(db_user)
    except IntegrityError:
        # Handle duplicate email constraint violation
        db.rollback()  # Roll back the failed transaction
        raise HTTPException(status_code=400, detail="Email already registered")

    # Return the created user data (password excluded)
    return UserResponse.from_orm(db_user)

@router.get("/users", response_model=List[UserResponse], summary="Get all users")
def get_users(db: Session = Depends(get_db)):
    """
    Retrieve all users from the database.

    Returns a list of all registered users with their id, name, and email.
    Passwords are excluded from the response for security.
    """
    # Query all users from the database
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse, summary="Get user by ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific user by their ID.

    - **user_id**: The unique identifier of the user

    Returns the user data with id, name, and email.

    Raises:
        HTTPException: If user with the given ID is not found (404 status)
    """
    # Query user by ID
    user = db.query(User).filter(User.id == user_id).first()

    # Check if user exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.put("/users/{user_id}", response_model=UserResponse, summary="Update a user")
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update an existing user's information.

    This endpoint allows updating the user's name, email, or password.
    Only the provided fields will be changed.

    Raises:
        HTTPException: If the user is not found or if the email already exists.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.email is not None:
        db_user.email = user_update.email
    if user_update.password is not None:
        db_user.password = hash_password(user_update.password)

    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

    return db_user