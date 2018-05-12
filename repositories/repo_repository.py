import logging

from database import (
    get_connection, repository_t
)

from .abstract_repository import AbstractRepository
from .cache import CoroutineSafeCache

log = logging.getLogger('application')


class RepoRepository(AbstractRepository):

    def __init__(self):
        self.cache = CoroutineSafeCache()
        super().__init__(repository_t)

    async def find(self, **kwargs):
        cache_key = self.get_cache_key_from_kwargs(prefix='find', **kwargs)
        if cache_key in self.cache:
            self.history.add_cached()
            return await self.cache.get(cache_key)
        with get_connection() as conn:
            whereclause = self.build_whereclause_from_kwargs(**kwargs)
            users = conn.execute(self.tbl.select().where(whereclause=whereclause)).fetchall()
            if users:
                await self.cache.setdefault(cache_key, users)
                self.history.add_successful()
            return users

    async def find_one(self, **kwargs):
        cache_key = self.get_cache_key_from_kwargs(prefix='find', **kwargs)
        if cache_key in self.cache:
            self.history.add_cached()
            return await self.cache.get(cache_key)
        with get_connection() as conn:
            whereclause = self.build_whereclause_from_kwargs(**kwargs)
            users = conn.execute(self.tbl.select().where(whereclause=whereclause)).fetchone()
            if users:
                await self.cache.setdefault(cache_key, users)
                self.history.add_successful()
            return users

    def __del__(self):
        log.info('Disposing RepoRepository instance. Info: %s. Cache size: %s', self.history, self.cache.size)
