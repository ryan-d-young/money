from sqlalchemy import MetaData, Table, Column, ForeignKey, types as t


def metadata(source: str):
    return MetaData(schema=f"raw_{source}")
