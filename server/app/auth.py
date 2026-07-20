import datetime
import os
from functools import wraps

import jwt
from flask import Blueprint, jsonify, request

from server.extensions import db
from app.models import User


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

    return jsonify(token=make_token(user.id), user_id=user.id), 200


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

