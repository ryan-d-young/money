from sqlalchemy import MetaData, Table, Column, ForeignKey, types as t

from .helpers import id_col


metadata = MetaData(schema="_meta")

_data_sources = Table(
    "data_sources", metadata, id_col(),
    Column("name", t.String),
    Column("metadata", t.JSON)
)
_data_routers = Table(
    "data_routers", metadata, id_col(),
    Column("name", t.String),
    Column("source", ForeignKey("data_sources.id")),
    Column("metadata", t.JSON)
)
_data_registry = Table(
    "data_registry", metadata, id_col(),
    Column("source", ForeignKey("data_sources.id")),
    Column("router", ForeignKey("data_routers.id")),
    Column("metadata", t.JSON),
    Column("request", t.JSON)
)
_data_collections = Table(
    "data_collections", metadata, id_col(),
    Column("name", t.String),
    Column("source", ForeignKey("data_sources.id")),
    Column("collection", t.ARRAY(t.String))
)