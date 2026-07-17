"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///atomic.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
config.py — backend environment configuration

This file will define configuration used by the Flask application.

Planned configuration:
- database URL
- JWT secret
- OpenAI API key
- Plaid client ID
- Plaid secret
- Plaid environment
- mock OpenAI flag
- mock Plaid flag
- frontend origin for CORS


"""
