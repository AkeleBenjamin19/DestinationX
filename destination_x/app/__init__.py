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

    # Register blueprints
    from .controllers.home_controller import home_bp
    app.register_blueprint(home_bp)

    from .controllers.preferences_controller import pref_bp
    app.register_blueprint(pref_bp)
    
    from .controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp)

    from .controllers.destination_controller import dest_bp
    app.register_blueprint(dest_bp)

    return app
app = create_app()

