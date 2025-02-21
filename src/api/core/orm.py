from datetime import datetime, timedelta

from sqlalchemy import Table, MetaData, ForeignKey, types as t
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declarative_base

metadata = MetaData(schema="meta")
metadata.create_schemas = True

base: DeclarativeBase = declarative_base(metadata=metadata)


class Providers(base):
    __tablename__ = "providers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    app_metadata: Mapped[dict] = mapped_column(t.JSON, default=dict)


class Collections(base):
    __tablename__ = "collections"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    provider_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.providers.id"))
    collection: Mapped[list[str]] = mapped_column(t.ARRAY(t.String))


class Schedule(base):
    __tablename__ = "schedule"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(t.String, ForeignKey("meta.providers.name"))
    router: Mapped[str] = mapped_column(t.String)
    collection: Mapped[str] = mapped_column(t.String, ForeignKey("meta.collections.name"), nullable=True)
    request: Mapped[dict] = mapped_column(t.JSON, default=dict)
    start: Mapped[datetime] = mapped_column(t.DateTime, default=datetime.now)
    end: Mapped[datetime] = mapped_column(t.DateTime, nullable=True)
    recurrence: Mapped[timedelta] = mapped_column(t.Interval, default=timedelta(days=1))


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
            await conn.run_sync(metadata.create_all)
            for meta in provider_metadata:
                await conn.run_sync(meta.create_all)    
        self._session = AsyncSession(dbengine)

    async def stop_db(self, commit: bool = True) -> None:
        if commit:
            await self.session.commit()
        await self.session.close()

    async def load_metadata(self, metadata: MetaData) -> None:
        await self.session.run_sync(metadata.create_all)

    def _table(self, table_name: str, metadata: MetaData) -> Table:
        table = Table(table_name, metadata, autoload_with=self.session.bind)
        return table
