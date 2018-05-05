import sqlalchemy as sa

from database import User


def cached(fn):  # todo cached decorator
    def wrapped(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapped


class UserRepository:

    cache = {}

    @classmethod
    def get_user_by_slack_id(cls, slack_id):
        return sa.select([User]).where(User.c.slack_id == slack_id).execute().fetchone()

    @classmethod
    def create_new_user(cls, **kwargs):
        return User.insert().values(**kwargs)

    @classmethod
    def get_user_by_github_username(cls, github_username):
        return sa.select([User]).where(User.c.github_username == github_username).execute().fetchone()
