import os

from sqlalchemy import create_engine

Engine = None

if os.environ.get('SQLALCHEMY_ENGINE'):
    Engine = create_engine(os.environ.get('SQLALCHEMY_ENGINE'), echo=bool(os.environ.get('DEBUG', False)))
else:
    raise Exception('Please define SQLAlchemy engine as environment variable')
