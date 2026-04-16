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

# Google Cloud BigQuery configuration
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "sales_dataset")
BIGQUERY_TABLE = os.getenv("BIGQUERY_TABLE", "sales_data")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")