from database.models import user_t, repository_t
from .engine import engine, meta


def create_database():
    meta.create_all(checkfirst=True)


def get_connection():
    return engine.connect()
