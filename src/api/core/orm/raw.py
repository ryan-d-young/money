from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, declarative_base
from sqlalchemy.sql import select

from .common import SelectFilter, filter_select


def metadata(provider_name: str) -> MetaData:
    return MetaData(schema=f"raw_{provider_name}")


def base(provider_name: str) -> DeclarativeBase:
    return declarative_base(metadata=metadata(provider_name))


async def fetch(
    session: AsyncSession,
    table: Table,
    *filters: SelectFilter,
) -> AsyncGenerator[dict, None]:
    query = select(table)
    query = filter_select(query, table, *filters)
    result = await session.execute(query)
    for row in result.scalars().all():
        yield row


async def fetch_one(
    session: AsyncSession,
    table: Table,
    *filters: SelectFilter,
) -> dict | None:
    query = select(table)
    query = filter_select(query, table, *filters)
    result = await session.execute(query)
    return result.scalars().one_or_none()


async def insert(
    session: AsyncSession,
    table: Table,
    *,
    do_update: bool = True,
    _commit: bool = True,
    **kwargs: dict[str, Any],
) -> None:
    query = pg_insert(table)
    if do_update:
        index_elements = [c.name for c in table.columns]
        set_ = {k: v for k, v in kwargs.items() if v is not None}
        query = query.on_conflict_do_update(
            index_elements=index_elements,
            set_=set_,
        )
    query = query.values(**kwargs)
    await session.execute(query)
    if _commit:
        await session.commit()


async def insert_many(
    session: AsyncSession,
    table: Table,
    *,
    do_update: bool = True,
    data: list[dict[str, Any]],
) -> None:
    for row in data:
        await insert(session, table, do_update=do_update, _commit=False, **row)
    await session.commit()
