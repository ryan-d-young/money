from typing import ClassVar
from datetime import datetime, timedelta

from sqlalchemy import MetaData, ForeignKey, types as t
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, AsyncConnection
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declarative_base
from sqlalchemy.sql import text

base_metadata = MetaData(schema="meta")
base_metadata.create_schemas = True
metadata: DeclarativeBase = declarative_base(metadata=base_metadata)


class Providers(metadata):
    __tablename__ = "providers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    app_metadata: Mapped[dict] = mapped_column(t.JSON)


class Collections(metadata):
    __tablename__ = "collections"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    provider_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.providers.id"))
    collection: Mapped[list[str]] = mapped_column(t.ARRAY(t.String))


class Schedule(metadata):
    __tablename__ = "schedule"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(t.String, ForeignKey("meta.providers.name"))
    router: Mapped[str] = mapped_column(t.String, nullable=True)
    collection: Mapped[str] = mapped_column(t.String, ForeignKey("meta.collections.name"), nullable=True)
    table_name: Mapped[str] = mapped_column(t.String, nullable=True)
    model_name: Mapped[str] = mapped_column(t.String, nullable=True)
    request: Mapped[dict] = mapped_column(t.JSON)
    start: Mapped[datetime] = mapped_column(t.DateTime)
    end: Mapped[datetime] = mapped_column(t.DateTime, nullable=True)
    recurrence: Mapped[timedelta] = mapped_column(t.Interval)


class OrmSessionMixin:
    _conn: AsyncConnection | None = None
    _session: AsyncSession | None = None

    @property
    def conn(self) -> AsyncConnection:
        if not self._conn:
            raise ValueError("Database connection not initialized")
        return self._conn

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            raise ValueError("Database session not initialized")
        return self._session

    async def init_db(self, dbengine: AsyncEngine, provider_metadata: list[MetaData]) -> None:        
        self._conn = dbengine.connect()
        await self._conn.start()
        self._session = AsyncSession(self.conn)

        schema = metadata.metadata.schema

        await self.session.run_sync(metadata.metadata.create_all)

        await self.conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

        for md in provider_metadata:
            if md.schema:
                await self.conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {md.schema}"))
        
        for md in provider_metadata:
            await self.session.run_sync(md.create_all)

    async def stop_db(self, commit: bool = True) -> None:
        if commit:
            await self.session.commit()
        await self.session.close()

    async def load_metadata(self, metadata: MetaData) -> None:
        await self.session.run_sync(metadata.create_all)
