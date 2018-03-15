import os

from sqlalchemy import create_engine

Engine = None

if os.environ.get('SQLALCHEMY_ENGINE'):
    Engine = create_engine(os.environ.get('SQLALCHEMY_ENGINE'),
                           pool_recycle=3600,
                           echo_pool=bool(os.environ.get('DEBUG', False)),
                           echo=bool(os.environ.get('DEBUG', False)))
else:
    raise Exception('Please define SQLAlchemy engine as environment variable')
