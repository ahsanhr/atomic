from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from app import create_app
from app.auth import make_token
from app.finance import check_spending_overage
from app.game_logic import streak_notification_content, update_login_streak
from app.models import Notification, User, UserGoal, UserRoomState
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


# helper so tests can make a user quickly
def _make_user(app, email="user@test.com", password="pw"):
    with app.app_context():
        user = User(username=email.split("@")[0], email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user.id, make_token(user.id)


# pure unit tests for streak logic no db needed


def test_first_login_gives_streak_1():
    streak, event = update_login_streak(0, None, date(2026, 7, 20))
    assert streak == 1
    assert event == "first_login"


def test_same_day_login_doesnt_change_streak():
    streak, event = update_login_streak(5, date(2026, 7, 20), date(2026, 7, 20))
    assert streak == 5
    assert event == "same_day"


def test_consecutive_day_increments_streak():
    streak, event = update_login_streak(3, date(2026, 7, 19), date(2026, 7, 20))
    assert streak == 4
    assert event == "continued"


def test_missed_day_resets_streak():
    streak, event = update_login_streak(10, date(2026, 7, 17), date(2026, 7, 20))
    assert streak == 1
    assert event == "reset"


def test_same_day_notification_content_is_none():
    assert streak_notification_content(5, "same_day") is None


def test_reset_notification_mentions_reset():
    title, message = streak_notification_content(1, "reset")
    assert "reset" in title.lower() or "reset" in message.lower()


def test_first_login_notification_has_welcome():
    title, _ = streak_notification_content(1, "first_login")
    assert "welcome" in title.lower() or "atomic" in title.lower()


def test_7_day_milestone_title_contains_7():
    title, _ = streak_notification_content(7, "continued")
    assert "7" in title


def test_regular_continued_streak_gets_generic_title():
    title, _ = streak_notification_content(4, "continued")
    assert "4" in title


# pure unit tests for spending overage


def _txn(amount, txn_date, flow_type="expense"):
    return SimpleNamespace(
        amount=amount,
        transaction_date=txn_date,
        flow_type=flow_type,
    )


def test_no_overage_when_under_both_goals():
    # 30 is under the weekly goal (300) and under the daily cap (300/7 ~= 42.86)
    txns = [_txn(30, date(2026, 7, 20))]
    result = check_spending_overage(txns, weekly_spending_goal=300, today=date(2026, 7, 20))
    assert result == []


def test_weekly_overage_detected():
    txns = [_txn(400, date(2026, 7, 20))]
    result = check_spending_overage(txns, weekly_spending_goal=300, today=date(2026, 7, 20))
    periods = [r["period"] for r in result]
    assert "weekly" in periods


def test_daily_overage_detected():
    # anything over weekly/7 triggers daily overage
    daily_goal = 300 / 7
    txns = [_txn(daily_goal + 10, date(2026, 7, 20))]
    result = check_spending_overage(txns, weekly_spending_goal=300, today=date(2026, 7, 20))
    assert any(r["period"] == "daily" for r in result)


def test_income_not_counted_toward_overage():
    txns = [_txn(9999, date(2026, 7, 20), flow_type="income")]
    result = check_spending_overage(txns, weekly_spending_goal=100, today=date(2026, 7, 20))
    assert result == []


def test_no_overage_when_goal_is_none():
    txns = [_txn(500, date(2026, 7, 20))]
    assert check_spending_overage(txns, weekly_spending_goal=None) == []


def test_no_overage_when_goal_is_zero():
    txns = [_txn(500, date(2026, 7, 20))]
    assert check_spending_overage(txns, weekly_spending_goal=0) == []


def test_old_transactions_not_counted_toward_weekly():
    # transaction from last week shouldnt count toward this weeks total
    last_week = date(2026, 7, 20) - timedelta(days=7)
    txns = [_txn(400, last_week)]
    result = check_spending_overage(txns, weekly_spending_goal=300, today=date(2026, 7, 20))
    assert result == []


# integration tests — verify notifications are written to db on login


def test_login_creates_first_login_notification(app, client):
    _make_user(app, email="a@test.com", password="pw")
    resp = client.post("/api/auth/login", json={"email": "a@test.com", "password": "pw"})
    assert resp.status_code == 200
    with app.app_context():
        count = Notification.query.filter_by(type="checkin_reminder").count()
    assert count == 1


def test_same_day_login_does_not_create_duplicate_notification(app, client):
    _make_user(app, email="b@test.com", password="pw")
    client.post("/api/auth/login", json={"email": "b@test.com", "password": "pw"})
    client.post("/api/auth/login", json={"email": "b@test.com", "password": "pw"})
    with app.app_context():
        count = Notification.query.filter_by(type="checkin_reminder").count()
    assert count == 1


def test_missed_day_resets_streak_and_creates_notification(app, client):
    user_id, _ = _make_user(app, email="c@test.com", password="pw")
    # simulate a login from 3 days ago
    with app.app_context():
        room = UserRoomState(
            user_id=user_id,
            login_streak=5,
            last_login_at=date(2026, 7, 17),
        )
        db.session.add(room)
        db.session.commit()

    client.post("/api/auth/login", json={"email": "c@test.com", "password": "pw"})

    with app.app_context():
        notif = Notification.query.filter_by(user_id=user_id).first()
        state = UserRoomState.query.filter_by(user_id=user_id).first()
    assert notif is not None
    assert "reset" in notif.title.lower() or "reset" in notif.message.lower()
    assert state.login_streak == 1
