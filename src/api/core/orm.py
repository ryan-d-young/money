from typing import ClassVar

from sqlalchemy import MetaData, ForeignKey, types as t
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declarative_base, relationship
from sqlalchemy.sql import text

base_metadata = MetaData(schema="meta")
base_metadata.create_schemas = True
metadata: DeclarativeBase = declarative_base(metadata=base_metadata)


class Providers(metadata):
    __tablename__ = "providers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    app_metadata: Mapped[dict] = mapped_column(t.JSON)
    routers: Mapped[list["Routers"]] = relationship(back_populates="provider")
    collections: Mapped[list["Collections"]] = relationship(back_populates="provider")
    requests: Mapped[list["Requests"]] = relationship(back_populates="provider")
    

class Routers(metadata):
    __tablename__ = "routers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    provider_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.providers.id"))
    provider: Mapped[Providers] = relationship(back_populates="routers")
    app_metadata: Mapped[dict] = mapped_column(t.JSON)
    requests: Mapped[list["Requests"]] = relationship(back_populates="router")


class Collections(metadata):
    __tablename__ = "collections"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    provider_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.providers.id"))
    provider: Mapped[Providers] = relationship(back_populates="collections")
    collection: Mapped[list[str]] = mapped_column(t.ARRAY(t.String))


class Requests(metadata):
    __tablename__ = "requests"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.providers.id"))
    router_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.routers.id"))
    provider: Mapped[Providers] = relationship(back_populates="requests")
    router: Mapped[Routers] = relationship(back_populates="requests")
    app_metadata: Mapped[dict] = mapped_column(t.JSON)
    request: Mapped[dict] = mapped_column(t.JSON)


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
