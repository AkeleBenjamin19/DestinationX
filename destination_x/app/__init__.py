"""Init file to create the app instance
This file contains the create_app function which creates the app instance.
"""

__author__ = "Akele Benjamin(620130803)"
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

# import flask migrate here
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    db.init_app(app)
    migrate.init_app(app, db)

    # Make sure all models are loaded:
    from app.models import Activity, City, Country, User, Visa_policies

    return app
app = create_app()

