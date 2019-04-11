from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from config.db import app_db

db = SQLAlchemy()


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config['CORS_ALLOW_HEADERS'] = "Content-Type"
    app.config['CORS_RESOURCES'] = {r"/api/*": {"origins": "*"}}
    app.config['SQLALCHEMY_DATABASE_URI'] = app_db.DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        # Imports
        from . import routes

        # Create tables for our models
        db.create_all()

        return app
