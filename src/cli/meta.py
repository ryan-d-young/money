import asyncio
import json
from typing import Annotated
from enum import Enum

import rich
import typer
from sqlalchemy.sql import select

from src.api import connect
app = typer.Typer(add_completion=False)


class TableOptions(str, Enum):
    providers = "providers"
    collections = "collections"
    schedule = "schedule"


@app.command(name="add")
def add(
    table: Annotated[TableOptions, typer.Argument(help="The table to add the record to")],
    data: Annotated[dict, typer.Argument(help="The data to add to the table", parser=json.loads)],
) -> None:
    async def _add():
        session = await connect()
        async with session.session.begin():
            await session.session.execute(
                session.table(table.value)
                .insert()
                .values(**data)
            )
    asyncio.run(_add())
    rich.print("Inserted: ", data)


@app.command(name="append")
def append(
    id: Annotated[int, typer.Argument(help="The id of the collection to append to")],
    item: Annotated[str, typer.Argument(help="The item to append to the collection")]
) -> None:
    async def _append():
        session = await connect()
        async with session.session.begin():
            result = await session.session.execute(
                select(session.table(TableOptions.collections))
                .where(session.table(TableOptions.collections).c.id == id)
            )
            collection = result.mappings().one_or_none()
            if collection is None:
                raise ValueError(f"Collection {id} not found")
            new_collection = collection['collection'] + [item]
            await session.session.execute(
                session.table(TableOptions.collections)
                .update()
                .where(session.table(TableOptions.collections).c.id == id)
                .values(collection=new_collection)
            )
    asyncio.run(_append())
    rich.print(f"Appended {item} to collection {id}")


@app.command(name="patch")
def patch(
    table: Annotated[TableOptions, typer.Argument(help="The table to update the record in")],
    id: Annotated[int, typer.Argument(help="The id of the record to update")],
    data: Annotated[dict, typer.Argument(help="The data to update the table with", parser=json.loads)],
) -> None:
    async def _patch():
        session = await connect()
        async with session.session.begin():
            result = await session.session.execute(
                select(session.table(table.value))
                .where(session.table(table.value).c.id == id)
            )
            record = result.mappings().one_or_none()
            if record is None:
                raise ValueError(f"Record {id} not found in table {table.value}")
            await session.session.execute(
                session.table(table.value)
                .update()
                .where(session.table(table.value).c.id == id)
                .values(**data)
            )
    asyncio.run(_patch())
    rich.print("Updated: ", data)


@app.command(name="list")
def list(
    table: Annotated[TableOptions, typer.Argument(help="The table to list the records from")],
) -> None:
    async def _list():
        session = await connect()
        async with session.session.begin():
            result = await session.session.execute(
                select(session.table(table.value))
            )
            records = result.mappings().all()
            return [{k: v for k, v in record.items()} for record in records]
    records = asyncio.run(_list())
    rich.print("Records:", *records)


@app.command(name="remove")
def remove(
    table: Annotated[TableOptions, typer.Argument(help="The table to delete the record from")],
    id: Annotated[int, typer.Argument(help="The id of the record to delete")],
) -> None:
    async def _remove():
        session = await connect()
        async with session.session.begin():
            await session.session.execute(
                session.table(table.value)
                .delete()
                .where(session.table(table.value).c.id == id)
            )
    asyncio.run(_remove())
    rich.print(f"Deleted record {id} from table {table.value}")


@app.command(name="metadata")
def provider_metadata(
    id: Annotated[int, typer.Argument(help="The id of the provider")],
    key: Annotated[str | None, typer.Option(help="The key to set or remove. If not provided, metadata is listed")] = None,
    value: Annotated[str | None, typer.Option(help="The value to set. If not provided, the value will be removed")] = None
) -> None:
    async def _set():
        session = await connect()
        async with session.session.begin():
            result = await session.session.execute(
                select(session.table(TableOptions.providers))
                .where(session.table(TableOptions.providers).c.id == id)
            )
            provider = result.mappings().one_or_none()
            if provider is None:
                raise ValueError(f"Provider {id} not found")
            
            if key is None:
                rich.print(provider["app_metadata"])
            else:
                metadata = dict(provider["app_metadata"])
                if value is None:
                    del metadata[key]
                    message = f"Removed metadata {key} for provider {id}"
                else:
                    metadata[key] = value
                    message = f"Set metadata {key}={value} for provider {id}"
                
                await session.session.execute(
                    session.table(TableOptions.providers)
                    .update()
                    .where(session.table(TableOptions.providers).c.id == id)
                    .values(app_metadata=metadata)
                )
                rich.print(message)
    asyncio.run(_set())


if __name__ == "__main__":
    asyncio.run(app())
