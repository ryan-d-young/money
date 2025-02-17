from typing import ClassVar
from datetime import datetime, timedelta

from sqlalchemy import MetaData, ForeignKey, types as t
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
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
    db_session: ClassVar[AsyncSession | None] = None

    async def init_db(self, dbengine: AsyncEngine, provider_metadata: list[MetaData]) -> "OrmSessionMixin":        
        async with dbengine.begin() as conn:
            schema = metadata.metadata.schema
            if schema:
                await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            
            for md in provider_metadata:
                if md.schema:
                    await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {md.schema}"))
            
            await conn.run_sync(metadata.metadata.create_all)
            for md in provider_metadata:
                await conn.run_sync(md.create_all)
                    
        self.db_session = AsyncSession(dbengine)        
        return self
    
    async def stop_db(self) -> "OrmSessionMixin":
        await self.db_session.close()
        return self

    @property
    def db(self) -> AsyncSession:
        if not self.db_session:
            raise ValueError("Database session not initialized")
        return self.db_session

    async def load_metadata(self, metadata: MetaData) -> None:
        async with self.db_session.begin() as conn:
            await conn.run_sync(metadata.create_all)
