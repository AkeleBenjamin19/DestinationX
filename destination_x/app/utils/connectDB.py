import os
from sqlalchemy import create_engine

user = os.environ.get("USER")
password = os.environ.get("PASSWORD")
host = os.environ.get("HOST")
port = os.environ.get("PORT")
database = os.environ.get("DATABASE")


def connect_db():
    # for creating connection string
    connection_str = f'postgresql:// {user}:{password}@{host}:{port}/{database}'
    # SQLAlchemy engine
    engine = create_engine(connection_str)
    # you can test if the connection is made or not
    try:
        with engine.connect() as connection_str:
            print('Successfully connected to the PostgreSQL database')
            return engine
    except Exception as ex:
        print(f'Sorry failed to connect: {ex}')
