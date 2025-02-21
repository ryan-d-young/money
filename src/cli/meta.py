import asyncio
import json
from typing import Annotated
from enum import Enum

import rich
import typer
from sqlalchemy.sql import insert

from .helpers import new_session

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
        session = await new_session()
        session_table = session.table(table.value)
        async with session.session.begin() as tr:
            await session.session.execute(insert(session_table), data)
            await tr.commit()
    asyncio.run(_add())
    rich.print("Inserted: ", data)


@app.command(name="patch")
async def patch(
    table: Annotated[TableOptions, typer.Argument(help="The table to update the record in")],
    data: Annotated[dict, typer.Argument(help="The data to update the table with", parser=json.loads)],
) -> None:
    ...


@app.command(name="list")
async def list(
    table: Annotated[TableOptions, typer.Argument(help="The table to list the records from")],
) -> None:
    ...


if __name__ == "__main__":
    asyncio.run(app())
