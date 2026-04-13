"""
Security utilities for password hashing and JWT token management.

This module provides functions for secure password handling using bcrypt
and JWT token creation for authentication.
"""

from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

# JWT configuration - TODO: Move SECRET_KEY to environment variables
SECRET_KEY = "supersecret"   # move to env later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    This function securely hashes passwords before storing them in the database.
    It automatically truncates passwords to 72 bytes to comply with bcrypt limits.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password string
    """
    # Truncate password to 72 bytes (bcrypt limit) and hash
    password = password.encode()[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Used during login to check if the provided password matches
    the stored hashed password.

    Args:
        plain: The plain text password to verify
        hashed: The hashed password from the database

    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    """
    Create a JWT access token.

    Generates a JSON Web Token containing the provided data plus an expiration time.
    Used for stateless authentication in API requests.

    Args:
        data: Dictionary containing data to encode in the token (e.g., user_id)

    Returns:
        The encoded JWT token string
    """
    # Create a copy of the data to avoid modifying the original
    to_encode = data.copy()

    # Set token expiration time
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Encode and return the JWT token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)