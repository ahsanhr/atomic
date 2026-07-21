"""External service wrappers for the backend."""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

class PlaidError(Exception):
    """An error returned while communicating with Plaid."""


def _plaid_request(path, data):
    client_id = os.getenv("PLAID_CLIENT_ID")
    secret = os.getenv("PLAID_SECRET")
    if not client_id or not secret:
        raise PlaidError("Plaid credentials are not configured")

    environment = os.getenv("PLAID_ENV", "sandbox").lower()
    if environment not in {"sandbox", "development", "production"}:
        raise PlaidError("PLAID_ENV must be sandbox, development, or production")

    url = f"https://{environment}.plaid.com{path}"
    payload = {"client_id": client_id, "secret": secret, **data}
    try:
        response = requests.post(url, json=payload, timeout=30)
        body = response.json()
    except (requests.RequestException, ValueError) as error:
        raise PlaidError("Plaid request failed") from error

    if response.status_code >= 400:
        error_code = body.get("error_code", "unknown_error")
        raise PlaidError(f"Plaid request failed: {error_code}")
    return body


def create_plaid_link_token(user_id):
    """Create the temporary token the frontend uses to open Plaid Link."""

    return _plaid_request(
        "/link/token/create",
        {
            "client_name": "Atomic",
            "user": {"client_user_id": str(user_id)},
            "products": ["transactions"],
            "country_codes": ["US"],
            "language": "en",
        },
    )


def create_sandbox_public_token():
    """Create a Sandbox Item without opening a real bank login screen."""

    if os.getenv("PLAID_ENV", "sandbox").lower() != "sandbox":
        raise PlaidError("Sandbox connection is only available when PLAID_ENV=sandbox")

    return _plaid_request(
        "/sandbox/public_token/create",
        {
            "institution_id": "ins_109508",
            "initial_products": ["transactions"],
            "options": {
                "override_username": "user_transactions_dynamic",
                "override_password": "sandbox_password",
            },
        },
    )


def exchange_plaid_public_token(public_token):
    """Exchange a temporary Link public token for an access token."""

    return _plaid_request(
        "/item/public_token/exchange",
        {"public_token": public_token},
    )


def sync_plaid_transactions(access_token, cursor=None):
    """Fetch the next page of transaction changes for a linked Item."""

    data = {"access_token": access_token}
    if cursor:
        data["cursor"] = cursor
    return _plaid_request("/transactions/sync", data)
