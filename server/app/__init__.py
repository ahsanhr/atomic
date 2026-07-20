"""
app package — Flask application setup

Planned responsibilities:
- create and configure the Flask application
- initialize SQLAlchemy
- initialize JWT authentication
- initialize CORS
- register the API routes
- make it possible to create separate development and test apps

"""

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from server.extensions import db, socketio


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, origins=app.config["FRONTEND_ORIGIN"])
    socketio.init_app(app, cors_allowed_origins=app.config["FRONTEND_ORIGIN"])

    from app.routes import api
    from app.auth import auth_bp
    from app.openai_service import openai_api
    from app.budget_routes import budget_api
    from app.plaid_routes import plaid_api
    __import__("app.socket_events")  # registers the connect/disconnect handlers

    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(auth_bp)
    app.register_blueprint(openai_api, url_prefix="/api")
    app.register_blueprint(budget_api, url_prefix="/api")
    app.register_blueprint(plaid_api)

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app
