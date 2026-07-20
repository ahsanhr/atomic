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

from datetime import date

from flask import Blueprint, jsonify

from app.auth import login_required
from app.finance import calculate_dashboard, check_spending_overage
from app.models import Notification, User, UserGoal, UserTransaction
from app.notification_routes import maybe_create_overage_notification
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

    all_txns = UserTransaction.query.filter_by(user_id=user_id).all()
    result = calculate_dashboard(all_txns)
    result["ai_summary"] = generate_financial_summary(result)

    # check if user went over their spending goals and notify if so
    goal = UserGoal.query.filter_by(user_id=user_id).first()
    if goal and goal.weekly_spending_goal:
        today = date.today()
        overages = check_spending_overage(all_txns, goal.weekly_spending_goal, today)
        if overages:
            maybe_create_overage_notification(db.session, user_id, overages, today)
            db.session.commit()

    result["notification_count"] = Notification.query.filter_by(
        user_id=user_id, is_read=False
    ).count()

    print(
        "[dashboard] income=${income:.2f} expenses=${expenses:.2f} net=${net:.2f} savings=${savings:.2f}".format(
            income=result["income"], expenses=result["expenses"], net=result["net_cash_flow"], savings=result["recommended_savings"]
        ),
        flush=True,
    )
    return jsonify(result)
