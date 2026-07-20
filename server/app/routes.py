"""
routes.py — Flask API endpoints

This file will contain one Blueprint for the minimal backend API.

Authentication endpoints:(Done in route.py now)
- POST /api/signup
  Creates a user account.

- POST /api/login
  Verifies credentials and returns a JWT.

Onboarding endpoint:
- POST /api/onboarding
  Accepts monthly income, necessary expenses, and current savings.
  Generates financial goals and initializes the user's level-1 room.

Dashboard endpoints:
- GET /api/dashboard
  Returns the combined user, goals, room, spending, and quest state.

- GET /api/room
  Returns the current level, XP, vitality, furniture, and friend.

Quest endpoints:
- GET /api/quests
  Returns fixed daily and weekly quests with completion state.

- POST /api/quests/<quest_key>/complete
  Records a completion and awards XP once per allowed period.
Plaid endpoints:
- POST /api/plaid/link-token
  Creates a Plaid Link token.

- POST /api/plaid/exchange
  Exchanges a Plaid public token for an access token.

- POST /api/plaid/sync
  Imports recent transactions without creating duplicates.

Development endpoint:
- POST /api/dev/run-daily-update
  Manually triggers consistency and vitality updates for the demo.


"""

from flask import Blueprint, jsonify

from app.auth import login_required
from app.finance import calculate_dashboard
from app.models import User, UserTransaction
from app.openai_service import generate_financial_summary
from server.extensions import db

api = Blueprint("api", __name__)


@api.get("/health")
def api_health():
    return jsonify(status="ok")


@api.get("/dashboard")
@login_required
def dashboard(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify(error="user not found"), 404
    result = calculate_dashboard(UserTransaction.query.filter_by(user_id=user_id).all())
    result["ai_summary"] = generate_financial_summary(result)
    print(
        "[dashboard] income=${income:.2f} expenses=${expenses:.2f} net=${net:.2f} savings=${savings:.2f}".format(
            income=result["income"], expenses=result["expenses"], net=result["net_cash_flow"], savings=result["recommended_savings"]
        ),
        flush=True,
    )
    return jsonify(result)
