"""Socket.IO event handlers for real time notifications."""

import os

import jwt
from flask_socketio import disconnect, emit, join_room

from server.extensions import socketio

secret = os.getenv("JWT_SECRET", "dev-jwt-secret")


@socketio.on("connect")
def handle_connect(auth):
    # client sends their JWT so we know which room to put them in
    token = (auth or {}).get("token", "")
    if not token:
        disconnect()
        return

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        disconnect()
        return

    # each user gets their own room so we can emit directly to them
    join_room(f"user_{user_id}")


@socketio.on("disconnect")
def handle_disconnect():
    pass


def emit_notification(user_id, notification_data):
    # send a notification event to just this user
    socketio.emit("notification", notification_data, room=f"user_{user_id}")
