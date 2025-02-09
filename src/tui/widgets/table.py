from textual.widgets import Table, ListView, TabPane
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src import db


class Schemas(ListView):
    async def load(self):
        self.items = await db.load_schemas()

    def render(self):
        return self.schema.__tablename__


class Tables(ListView):
    def __init__(self, schema: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema

    async def load(self):
        self.items = await db.load_tables(self.schema)

    def render(self):
        return self.table.__tablename__


class Table(Table):
    def __init__(self, schema: str, table: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema
        self.table = table

    async def load(self, session: AsyncSession):
        table = await db.read(self.schema, self.table, session)


class TablePane(TabPane):
    def __init__(self, schema: str, table: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema
        self.table = table

    async def on_schemas_select(self, event: Select):
        self.table = Tables(self.schema)
        await self.table.load()
        self.app.push_tab(self)

    async def on_tables_select(self, event: Select):
        self.table = Table(self.schema, self.table)
        await self.table.load()
        self.app.push_tab(self)

    async def on_table_select(self, event: Select):
        self.table = Table(self.schema, self.table)
        await self.table.load()

    def compose(self):
        yield Vertical(
            Schemas(on_select=self.on_schemas_select),
            Tables(on_select=self.on_tables_select),
            Table(on_select=self.on_table_select),
        )
