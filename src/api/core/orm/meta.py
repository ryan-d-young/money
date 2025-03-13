from datetime import timedelta, time

from sqlalchemy import ForeignKey, MetaData
from sqlalchemy import types as t
from sqlalchemy.dialects.postgresql import TIME
from sqlalchemy.orm import DeclarativeBase, Mapped, declarative_base, mapped_column

metadata = MetaData(schema="meta")
base: DeclarativeBase = declarative_base(metadata=metadata)


class Providers(base):
    __tablename__ = "providers"
    id: Mapped[int] = mapped_column(t.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(t.String, unique=True)
    app_metadata: Mapped[dict] = mapped_column(t.JSON, default=dict)


class Collections(base):
    __tablename__ = "collections"
    id: Mapped[int] = mapped_column(t.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(t.String, unique=True)
    provider_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.providers.id"), nullable=True)


class CollectionItems(base):
    __tablename__ = "collection_items"
    id: Mapped[int] = mapped_column(t.Integer, primary_key=True, autoincrement=True)
    provider_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.providers.id"))
    collection_id: Mapped[int] = mapped_column(t.Integer, ForeignKey("meta.collections.id"))
    name: Mapped[str] = mapped_column(t.String)


class Schedule(base):
    __tablename__ = "schedule"
    id: Mapped[int] = mapped_column(t.Integer, primary_key=True, autoincrement=True)
    enabled: Mapped[bool] = mapped_column(t.Boolean, default=True)
    provider: Mapped[str] = mapped_column(t.String, ForeignKey("meta.providers.name"))
    router: Mapped[str] = mapped_column(t.String)
    request: Mapped[dict] = mapped_column(t.JSON, default=dict)
    start: Mapped[time] = mapped_column(TIME, nullable=True)
    end: Mapped[time] = mapped_column(TIME, nullable=True)
    interval: Mapped[timedelta] = mapped_column(TIME, default=timedelta(days=1))
