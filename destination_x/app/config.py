import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env if it exists.

class Config(object):
    """Base Config Object"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('CONNECTION_STR', '').replace('postgres://', 'postgresql://')

    SQLALCHEMY_TRACK_MODIFICATIONS = False # This is just here to suppress a warning from SQLAlchemy as it will soon be removed