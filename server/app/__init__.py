"""
app package — Flask application setup

This file will contain the Flask application factory.

Planned responsibilities:
- create and configure the Flask application
- initialize SQLAlchemy
- initialize JWT authentication
- initialize CORS
- register the API routes
- make it possible to create separate development and test apps

No application setup should be implemented yet.
"""

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app, origins=app.config["FRONTEND_ORIGIN"])

    from app.routes import api

    app.register_blueprint(api, url_prefix="/api")

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app
