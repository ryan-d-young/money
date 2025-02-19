from datetime import datetime, timedelta

from sqlalchemy import MetaData, ForeignKey, types as t
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declarative_base

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
    _session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            raise ValueError("Database session not initialized")
        return self._session

    async def init_db(
        self,
        dbengine: AsyncEngine,
        provider_metadata: list[DeclarativeBase],
    ) -> None:
        """Initialize the database connection."""
        async with dbengine.begin() as conn:
            await conn.run_sync(base_metadata.create_all)
            for meta in provider_metadata:
                await conn.run_sync(meta.create_all)    
        self._session = AsyncSession(dbengine)

    async def stop_db(self, commit: bool = True) -> None:
        if commit:
            await self.session.commit()
        await self.session.close()

    async def load_metadata(self, metadata: MetaData) -> None:
        await self.session.run_sync(metadata.create_all)
