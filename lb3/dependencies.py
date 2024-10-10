from aioodbc import Connection
from fastapi import Depends

from lb3.db import DatabasePool


async def db_connection() -> Connection:
    async with DatabasePool.get_instance().acquire() as conn:
        yield conn


DbConnectionDep: Connection = Depends(db_connection)
