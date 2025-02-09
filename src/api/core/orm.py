from sqlalchemy import MetaData, Table, Column, ForeignKey, types as t

metadata = MetaData(schema="_meta")

metadata_tables = {
    "data_sources": Table(
        "data_sources", metadata, 
        Column("id", t.Integer, primary_key=True, autoincrement=True),
        Column("name", t.String),
        Column("metadata", t.JSON)
    ),
    "data_routers": Table(
        "data_routers", metadata, 
        Column("id", t.Integer, primary_key=True, autoincrement=True),
        Column("name", t.String),
        Column("source", ForeignKey("data_sources.id")),
        Column("metadata", t.JSON)
    ),
    "data_registry": Table(
        "data_registry", metadata, 
        Column("id", t.Integer, primary_key=True, autoincrement=True),
        Column("source", ForeignKey("data_sources.id")),
        Column("router", ForeignKey("data_routers.id")),
        Column("metadata", t.JSON),
        Column("request", t.JSON)
    ),
    "data_collections": Table(
        "data_collections", metadata, 
        Column("id", t.Integer, primary_key=True, autoincrement=True),
        Column("name", t.String),
        Column("source", ForeignKey("data_sources.id")),
        Column("collection", t.ARRAY(t.String))
    )
}


def schema(source: str):
    return MetaData(schema=f"raw_{source}")
