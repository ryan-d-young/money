from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession


def parse_table(session: AsyncSession, table: str) -> DeclarativeBase:
    return session.query(table).all()


async def new_session():
    from src.api import connect
    session = await connect()
    return session
