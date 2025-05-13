# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

# module‐level extensions
db      = SQLAlchemy()
migrate = Migrate()

def create_app():
    # 1) build the Flask app
    app = Flask(__name__)
    app.config.from_object(Config)

    # 2) initialize extensions with this app
    db.init_app(app)
    migrate.init_app(app, db)

    

    # 4) register your blueprints on *this* app instance
    from .controllers.home_controller import home_bp
    app.register_blueprint(home_bp)

    return app
