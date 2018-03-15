from sqlalchemy.orm import Session as SqlAlchemySession

from database.models import Base, User, GithubRepo
from .engine import Engine

Base.metadata.create_all(Engine)
Session = SqlAlchemySession(bind=Engine)
