from sqlalchemy import MetaData


def metadata(source: str):
    return MetaData(schema=f"raw_{source}")
