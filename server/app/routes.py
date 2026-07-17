"""
routes.py — Flask API endpoints

This file will contain one Blueprint for the minimal backend API.

Authentication endpoints:
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

api = Blueprint("api", __name__)


@api.get("/health")
def api_health():
    return jsonify(status="ok")
