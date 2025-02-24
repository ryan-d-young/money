from datetime import datetime, timedelta
from os import name

from sqlalchemy import ForeignKey, MetaData
from sqlalchemy import types as t
from sqlalchemy.orm import DeclarativeBase, Mapped, declarative_base, mapped_column

metadata = MetaData(schema="meta")
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
    provider_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.providers.id"), nullable=True)


class CollectionItems(base):
    __tablename__ = "collection_items"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.providers.id"))
    collection_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.collections.id"))
    name: Mapped[str] = mapped_column(t.String)


class Registry(base):
    __tablename__ = "registry"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(t.String, ForeignKey("meta.providers.name"))
    router: Mapped[str] = mapped_column(t.String)
    collection: Mapped[str] = mapped_column(t.String, ForeignKey("meta.collections.name"), nullable=True)
    request: Mapped[dict] = mapped_column(t.JSON, default=dict)
    start: Mapped[datetime] = mapped_column(t.DateTime, default=datetime.now)
    end: Mapped[datetime] = mapped_column(t.DateTime, nullable=True)
    recurrence: Mapped[timedelta] = mapped_column(t.Interval, default=timedelta(days=1))
