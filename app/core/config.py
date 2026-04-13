"""
Application configuration settings.

This module loads environment variables and provides configuration
values used throughout the application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection URL loaded from environment variables
# This should be set in the .env file for security
DATABASE_URL = os.getenv("DATABASE_URL")