from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import select, insert, delete


async def create(table: DeclarativeBase, session: AsyncSession) -> None:
    async with session.begin() as tr:
        tr.add(table)
        await tr.commit()


async def read(table: DeclarativeBase, session: AsyncSession, **kwargs) -> list[DeclarativeBase]:
    async with session.begin() as tr:
        stmt = select(table).where(**kwargs)
        result = await tr.execute(stmt)
        return result.scalars().all()


async def update(table: DeclarativeBase, session: AsyncSession, **kwargs) -> None:
    async with session.begin() as tr:
        stmt = insert(table).values(**kwargs)
        await tr.execute(stmt)
        await tr.commit()


async def delete(table: DeclarativeBase, session: AsyncSession) -> None:
    async with session.begin() as tr:
        stmt = delete(table)
        await tr.execute(stmt)
        await tr.commit()
