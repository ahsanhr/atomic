import datetime
import os
from datetime import date
from functools import wraps

import jwt
from flask import Blueprint, jsonify, request

from server.extensions import db
from app.models import Notification, User, UserRoomState
from app.game_logic import award_xp, calculate_login_xp, streak_notification_content, update_login_streak
from app.quest_helpers import check_spending_quest, check_weekly_login_quest, complete_quest, track_login_day
from app.socket_events import emit_notification


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
secret = os.getenv("JWT_SECRET", "dev-jwt-secret")


def make_token(user_id):
    """Create a token that is valid for 24 hours."""

    payload = {
        "sub": str(user_id),
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify(error="missing token"), 401

        token = header.split(" ", 1)[1].strip()
        if not token:
            return jsonify(error="missing token"), 401

        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            kwargs["user_id"] = int(payload["sub"])
        except jwt.ExpiredSignatureError:
            return jsonify(error="token expired, please log in again"), 401
        except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
            return jsonify(error="invalid token"), 401

        return view(*args, **kwargs)

    return wrapper


@auth_bp.post("/signup")
def signup():
    body = request.get_json(silent=True) or {}
    username = body.get("username", "").strip()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not username or not email or not password:
        return jsonify(error="username, email, and password are all required"), 400

    taken = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()
    if taken:
        return jsonify(error="username or email already taken"), 409

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(token=make_token(new_user.id), user_id=new_user.id), 201


@auth_bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or user.password != password:
        return jsonify(error="invalid email or password"), 401

    today = date.today()

    # load or create room state so we can track the streak
    room_state = UserRoomState.query.filter_by(user_id=user.id).first()
    if room_state is None:
        room_state = UserRoomState(user_id=user.id)
        db.session.add(room_state)

    new_streak, event = update_login_streak(
        room_state.login_streak or 0,
        room_state.last_login_at,
        today,
    )

    if event != "same_day":
        room_state.login_streak = new_streak
        room_state.last_login_at = today

        content = streak_notification_content(new_streak, event)
        if content is not None:
            title, message = content
            notif_type = "streak_update" if event == "continued" else "checkin_reminder"
            notif = Notification(
                user_id=user.id,
                type=notif_type,
                title=title,
                message=message,
            )
            db.session.add(notif)
            db.session.flush()  # get the id before commit
            emit_notification(user.id, {
                "id": notif.id,
                "type": notif.type,
                "title": notif.title,
                "message": notif.message,
                "is_read": False,
            })

        # award login xp and run auto quest checks
        login_xp = calculate_login_xp(new_streak)
        new_xp, new_level, _ = award_xp(room_state.current_xp or 0, login_xp)
        room_state.current_xp = new_xp
        room_state.current_level = new_level

        track_login_day(db.session, user.id, today)
        complete_quest(db.session, room_state, user.id, "view_finance_tip", today)
        check_spending_quest(db.session, room_state, user.id, today)
        check_weekly_login_quest(db.session, room_state, user.id, today)

        db.session.commit()

    unread_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()

    return jsonify(
        token=make_token(user.id),
        user_id=user.id,
        notification_count=unread_count,
    ), 200


@auth_bp.get("/me")
@login_required
def get_current_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify(error="user not found"), 404

    return jsonify(
        user_id=user.id,
        username=user.username,
        email=user.email,
    ), 200

