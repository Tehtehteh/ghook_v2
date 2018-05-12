import asyncio


class CoroutineSafeCache(dict):

    def __init__(self, **kwargs):
        self._lock = asyncio.Lock()
        super().__init__(**kwargs)

    @property
    def locked(self):
        return self._lock.locked()

    @property
    def size(self):  # todo Memoized Property
        return self.__sizeof__()

    async def get(self, key, default=None):
        async with self._lock:
            res = super().get(key, default)
        return res

    async def setdefault(self, key, default=None):
        async with self._lock:
            res = super().setdefault(key, default)
        return res

    async def flush(self):
        async with self._lock:
            super().clear()
