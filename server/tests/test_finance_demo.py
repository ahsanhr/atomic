from datetime import date
from types import SimpleNamespace

import pytest

from app import create_app
from app.auth import make_token
from app.finance import calculate_dashboard, classify_transaction
from app.models import PlaidItem, User, UserGoal, UserTransaction
from server.extensions import db


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = "http://localhost:5173"


@pytest.fixture
def app():
    application = create_app(TestConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_classification_rules():
    assert classify_transaction({"description": "SEO Tech Developer Payroll"})[0] == "income"
    assert classify_transaction({"description": "Interest Payment", "personal_finance_category": {"primary": "INCOME"}})[0] == "income"
    assert classify_transaction({"description": "Direct Deposit"})[0] == "income"
    assert classify_transaction({"description": "Account Credit", "amount": -125.50})[0] == "income"
    assert classify_transaction({"description": "Trader Joe's"})[0] == "expense"
    assert classify_transaction({"description": "Checking to Savings Transfer"})[0] == "transfer"
    assert classify_transaction({"description": "Credit Card Payment"})[0] == "payment"
    assert classify_transaction({"description": "Merchant Refund"})[0] == "refund"
    assert classify_transaction({})[0] == "ignored"


def test_dashboard_excludes_transfers_and_payments_and_applies_refunds():
    rows = [
        SimpleNamespace(amount=-2000, flow_type="income", app_category="income", category=None, merchant_name="SEO", original_name="SEO", transaction_date=date(2026, 7, 1), plaid_transaction_id="1"),
        SimpleNamespace(amount=100, flow_type="expense", app_category="groceries", category=None, merchant_name="Trader Joe's", original_name="Trader Joe's", transaction_date=date(2026, 7, 2), plaid_transaction_id="2"),
        SimpleNamespace(amount=20, flow_type="refund", app_category="refund", category=None, merchant_name="Merchant Refund", original_name="Merchant Refund", transaction_date=date(2026, 7, 3), plaid_transaction_id="3"),
        SimpleNamespace(amount=500, flow_type="transfer", app_category="transfer", category=None, merchant_name="Transfer", original_name="Transfer", transaction_date=date(2026, 7, 4), plaid_transaction_id="4"),
        SimpleNamespace(amount=400, flow_type="payment", app_category="payment", category=None, merchant_name="Credit Card Payment", original_name="Credit Card Payment", transaction_date=date(2026, 7, 5), plaid_transaction_id="5"),
    ]
    result = calculate_dashboard(rows)
    assert result["income"] == 2000
    assert result["expenses"] == 80
    assert result["net_cash_flow"] == 1920
    assert result["recommended_savings"] == 400


def test_sync_saves_classification_and_does_not_duplicate(app, client, monkeypatch):
    from app import plaid_routes

    with app.app_context():
        user = User(email="sync@example.com", username="sync", password="secret")
        db.session.add(user)
        db.session.flush()
        item = PlaidItem(user_id=user.id, item_id="item-2", access_token="access-2")
        db.session.add(item)
        db.session.commit()
        token = make_token(user.id)

    response_data = {
        "added": [{
            "transaction_id": "tx-1", "amount": 2000, "date": "2026-07-01",
            "name": "SEO Tech Developer Payroll", "merchant_name": "SEO",
        }],
        "modified": [], "removed": [], "has_more": False, "next_cursor": "cursor-1",
    }
    monkeypatch.setattr(plaid_routes, "sync_plaid_transactions", lambda access, cursor: response_data)
    assert client.post("/api/plaid/sync", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    assert client.post("/api/plaid/sync", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    with app.app_context():
        assert UserTransaction.query.count() == 1
        assert UserTransaction.query.first().flow_type == "income"


def test_sandbox_connection_does_not_create_a_second_item(app, client, monkeypatch):
    from app import plaid_routes

    with app.app_context():
        user = User(email="sandbox@example.com", username="sandbox", password="secret")
        db.session.add(user)
        db.session.flush()
        db.session.add(PlaidItem(user_id=user.id, item_id="sandbox-item", access_token="sandbox-access"))
        db.session.add(UserTransaction(user_id=user.id, plaid_transaction_id="sandbox-tx", amount=100))
        db.session.commit()
        token = make_token(user.id)

    monkeypatch.setattr(
        plaid_routes,
        "create_sandbox_public_token",
        lambda: pytest.fail("a second Sandbox Item should not be created"),
    )
    response = client.post(
        "/api/plaid/sandbox-token",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.get_json() == {"already_connected": True}


def test_dashboard_endpoint_contains_savings_and_ai_fallback(app, client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with app.app_context():
        user = User(email="dash@example.com", username="dash", password="secret")
        db.session.add(user)
        db.session.flush()
        db.session.add(UserGoal(user_id=user.id, monthly_savings_goal=50))
        db.session.add(UserTransaction(user_id=user.id, plaid_transaction_id="tx-2", amount=2000, flow_type="income", app_category="income", merchant_name="SEO", transaction_date=date(2026, 7, 1)))
        db.session.add(UserTransaction(user_id=user.id, plaid_transaction_id="tx-3", amount=500, flow_type="expense", app_category="rent", merchant_name="Rent", transaction_date=date(2026, 7, 2)))
        db.session.commit()
        token = make_token(user.id)

    response = client.get("/api/dashboard", headers={"Authorization": f"Bearer {token}"})
    body = response.get_json()
    assert response.status_code == 200
    assert body["income"] == 2000
    assert body["expenses"] == 500
    assert body["recommended_savings"] == 400
    assert set(body["ai_summary"]) == {"summary", "improvement", "encouragement"}
