"""
run.py — Flask development entry point

This file will create the Flask app through the application factory and make
it available to the Flask development server.

No server startup implementation should be added yet.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app
from server.extensions import socketio

app = create_app()


if __name__ == "__main__":
    socketio.run(
        app,
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )
