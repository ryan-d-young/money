from sqlalchemy import MetaData

from .engine import AsyncDatabaseManager


async def create_meta(db: AsyncDatabaseManager, meta: MetaData):
    async with db.connection() as conn:
        await meta.create_all(conn)


