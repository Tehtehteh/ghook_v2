import logging

import sqlalchemy as sa

from database import user_t, get_connection

from .cache import CoroutineSafeCache
from .abstract_repository import AbstractRepository

log = logging.getLogger('application')


class UserRepository(AbstractRepository):

    def __init__(self):
        self.cache = CoroutineSafeCache()
        super().__init__(user_t)

    async def create(self, **kwargs):
        if not self.validate_kwargs_against_table(**kwargs):
            self.history.add_failed()
            raise Exception(f'Kwargs are not valid for target table {kwargs}')
        with get_connection() as conn:
            user = conn.execute(self.tbl.insert().values(**kwargs))
            self.history.add_successful()
            return user

    async def update(self, values=None, **kwargs):
        if not values:
            log.error('No values received to update user model.')
            return
        whereclause = self.build_whereclause_from_kwargs(**kwargs)
        with get_connection() as conn:
            conn.execute(self.tbl.update(whereclause).values(values))
            self.history.add_successful()
            await self.cache.flush()

    async def find(self, with_cache=False, **kwargs):
        if with_cache:
            cache_key = self.get_cache_key_from_kwargs(prefix='find', **kwargs)
            if cache_key in self.cache:
                self.history.add_cached()
                return await self.cache.get(cache_key)
        with get_connection() as conn:
            whereclause = self.build_whereclause_from_kwargs(**kwargs)
            users = conn.execute(self.tbl.select().where(whereclause=whereclause)).fetchall()
            if users:
                self.history.add_successful()
                if with_cache and cache_key:
                    await self.cache.setdefault(cache_key, users)
            return users

    async def find_one(self, **kwargs):
        cache_key = self.get_cache_key_from_kwargs(prefix='find_one', **kwargs)
        if cache_key in self.cache:
            self.history.add_cached()
            return await self.cache.get(cache_key)
        with get_connection() as conn:
            whereclause = self.build_whereclause_from_kwargs(**kwargs)
            user = conn.execute(self.tbl.select().where(whereclause=whereclause)).fetchone()
            if user:
                await self.cache.setdefault(cache_key, user)
                self.history.add_successful()
            return user

    @classmethod
    def get_user_by_slack_id(cls, slack_id):
        return sa.select([user_t]).where(user_t.c.slack_id == slack_id).execute().fetchone()

    @classmethod
    def create_new_user(cls, **kwargs):
        return user_t.insert().values(**kwargs)

    @classmethod
    def get_user_by_github_username(cls, github_username):
        return sa.select([user_t]).where(user_t.c.github_username == github_username).execute().fetchone()

    def __del__(self):
        log.info('Disposing UserRepository instance. Info: %s. Cache size: %s', self.history, self.cache.size)
