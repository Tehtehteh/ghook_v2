from sqlalchemy.orm import Session as SqlAlchemySession

from .users import User
from .base import Base
from .engine import Engine

Base.metadata.create_all(Engine)
Session = SqlAlchemySession(bind=Engine)
