from sqlalchemy import Column, Integer, String

from .base import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

    slack_id = Column(String(100))
    slack_username = Column(String(100), default=None)
    slack_dm_id = Column(String(100), default=None)

    github_username = Column(String(100), default=None)
    github_email = Column(String(100), default=None)

    def __repr__(self):
        return f'<User obj id={self.id}, slack_id={self.slack_id} '\
               f'slack_dm_id={self.slack_dm_id}, github_username={self.github_username}'
