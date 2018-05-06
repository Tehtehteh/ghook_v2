import sqlalchemy as sa

from database import User


def cached(fn):  # todo cached decorator
    def wrapped(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapped


class History(object):

    def __init__(self):
        self.failed = 0
        self.successful = 0

    def add_successful(self):
        self.successful += 1

    def add_failed(self):
        self.failed += 1

    def __str__(self):
        msg = ''
        if self.failed:
            msg = f'WARNING: Failed {self.failed} queries.'
        msg += f'Successful: {self.successful} queries.'
        return msg


class UserRepository(object):

    def __init__(self):
        self.history = History()

    # def find(self, **kwargs): ...  #todo !!!
        # with get_connection() as conn:
        #     self.history.add_successful()


    @classmethod
    def get_user_by_slack_id(cls, slack_id):
        return sa.select([User]).where(User.c.slack_id == slack_id).execute().fetchone()

    @classmethod
    def create_new_user(cls, **kwargs):
        return User.insert().values(**kwargs)

    @classmethod
    def get_user_by_github_username(cls, github_username):
        return sa.select([User]).where(User.c.github_username == github_username).execute().fetchone()

