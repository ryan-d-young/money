from sqlalchemy import MetaData, Pool
from sqlalchemy.ext.asyncio import create_async_pool_from_url, AsyncEngine, AsyncTransaction

from .engine import AsyncDatabaseManager


async def create_meta(db: AsyncDatabaseManager, meta: MetaData):
    async with db.connection() as conn:
        await meta.create_all(conn)