from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql import text


async def load_schemas(engine: AsyncEngine) -> list[str]:
    async with engine.begin() as conn:
        stmt = text("SELECT schema_name FROM information_schema.schemata")
        result = await conn.execute(stmt)
        return result.scalars().all()


async def load_tables(engine: AsyncEngine, schema: str) -> list[str]:
    async with engine.begin() as conn:
        stmt = text(
            f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}'"
        )
        result = await conn.execute(stmt)
        return result.scalars().all()
