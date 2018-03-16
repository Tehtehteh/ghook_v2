from sqlalchemy import Column, Integer, String, ForeignKey

from .base import Base


class GithubRepo(Base):
    __tablename__ = 'repositories'
    id = Column(Integer, primary_key=True)
    subscribed_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))
    repo_url = Column(String(100), nullable=False)
    repo_type = Column(String(100), default='github')

    def __repr__(self):
        return f'<GitHub repo obj id={self.id}, repo_url={self.repo_url}>'
