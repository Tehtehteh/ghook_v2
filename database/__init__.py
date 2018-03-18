from database.models import User, Repository
from .engine import engine, meta


def init():
    meta.create_all(checkfirst=True)
