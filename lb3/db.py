from __future__ import annotations
from contextlib import asynccontextmanager

import aioodbc


class DatabasePool:
    _instance: DatabasePool | None = None

    def __init__(self, dsn: str):
        self._dsn = dsn
        self._pool: aioodbc.Pool | None = None

    def __new__(cls, *args, **kwargs) -> DatabasePool:
        if not isinstance(cls._instance, cls):
            cls._instance = super(cls.__class__, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> DatabasePool:
        return cls._instance

    @asynccontextmanager
    async def acquire(self) -> aioodbc.Connection:
        if self._pool is None:
            self._pool = await aioodbc.create_pool(self._dsn)

        async with self._pool.acquire() as conn:
            yield conn
