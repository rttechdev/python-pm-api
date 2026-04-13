"""
Pydantic schemas for user data validation and serialization.

This module defines the data models used for API request/response validation
and serialization. It ensures data integrity and provides automatic validation.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    """
    Schema for user creation requests.

    Used to validate incoming data when creating new users.
    Includes password validation for security requirements.
    """
    name: str
    email: EmailStr  # Automatically validates email format
    password: str

    @validator('password')
    def password_length(cls, v):
        """
        Validate password length and byte size.

        Ensures passwords meet minimum security requirements and
        don't exceed bcrypt's 72-byte limit.

        Args:
            v: The password string to validate

        Returns:
            The validated password string

        Raises:
            ValueError: If password is too short or too long
        """
        if len(v.encode()) > 72:
            raise ValueError('Password cannot be longer than 72 bytes')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserUpdate(BaseModel):
    """
    Schema for user update requests.

    All fields are optional so that a client can update one or more values.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @validator('password')
    def password_length(cls, v):
        if v is None or v == "":
            return None
        if len(v.encode()) > 72:
            raise ValueError('Password cannot be longer than 72 bytes')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserResponse(BaseModel):
    """
    Schema for user response data.

    Used to serialize user data in API responses.
    Excludes sensitive information like passwords.
    """
    id: int
    name: str
    email: EmailStr

    class Config:
        # Allow conversion from SQLAlchemy ORM objects
        from_attributes = True