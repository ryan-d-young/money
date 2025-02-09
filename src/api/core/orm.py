from sqlalchemy import MetaData, Table, Column, ForeignKey, types as t

metadata = MetaData(schema="_meta")

metadata_tables = {
    "data_providers": Table(
        "data_providers", metadata, 
        Column("id", t.Integer, primary_key=True, autoincrement=True),
        Column("name", t.String),
        Column("metadata", t.JSON)
    ),
    "data_routers": Table(
        "data_routers", metadata, 
        Column("id", t.Integer, primary_key=True, autoincrement=True),
        Column("name", t.String),
        Column("provider", ForeignKey("data_providers.id")),
        Column("metadata", t.JSON)
    ),
    "data_registry": Table(
        "data_registry", metadata, 
        Column("id", t.Integer, primary_key=True, autoincrement=True),
        Column("provider", ForeignKey("data_providers.id")),
        Column("router", ForeignKey("data_routers.id")),
        Column("metadata", t.JSON),
        Column("request", t.JSON)
    ),
    "data_collections": Table(
        "data_collections", metadata, 
        Column("id", t.Integer, primary_key=True, autoincrement=True),
        Column("name", t.String),
        Column("provider", ForeignKey("data_providers.id")),
        Column("collection", t.ARRAY(t.String))
    )
}


def schema(source: str):
    return MetaData(schema=f"raw_{source}")
