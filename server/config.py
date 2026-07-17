"""
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

Secrets must come from environment variables and must not be committed.
Separate development and testing configuration may be added later.
"""
