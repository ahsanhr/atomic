"""
run.py — Flask development entry point

This file will create the Flask app through the application factory and make
it available to the Flask development server.

No server startup implementation should be added yet.
"""

from app import create_app
from server.extensions import socketio

app = create_app()


if __name__ == "__main__":
    socketio.run(app, debug=True)
