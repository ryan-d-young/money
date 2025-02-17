from typing import Any

from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.ext.asyncio import AsyncSession
from textual import work
from textual.validation import ValidationResult, Validator
from textual.widgets import Button, DataTable, Input, Select, TabPane as TabPane_

from src import api
from util import dt


class DateTimeInput(Input):
    class DateTimeValidator(Validator):
        def validate(self, value: str) -> ValidationResult:
            try:
                dt.convert(d_str=value)
            except ValueError:
                return self.failure("Invalid date/time")
            return self.success()

    def __init__(self, name: str):
        super().__init__(
            placeholder=dt._ISODATE,
            validators=(self.DateTimeValidator(),),
            id=f"datetime-input-{name}",
        )


class DictSelector(Select):
    def __init__(self, name: str, **kwargs: dict[str, Any]):
        super().__init__(
            options=list(kwargs.keys()), prompt=name, id=f"selector-{name}"
        )
        self._map = kwargs

    def value(self) -> str:
        return self._map[super().value]


class TableDisplayRowDeleteButton(Button):
    def __init__(self, key: str):
        super().__init__(label="-", id=f"delete-button-{key}", variant="error")
        self.key = key

    def on_click(self) -> None:
        self.parent.remove_row(self.key)


class TableDisplay(DataTable):
    @work
    async def load_table(self) -> list[tuple]:
        return await self.app.session.session.refresh(self._table)

    @work
    async def insert_row(self, row: tuple) -> None:
        await self.app.session.session.add(self._table(*row))

    @work
    async def update_row(self, row: tuple) -> None:
        await self.app.session.session.merge(self._table(*row))

    @work
    async def delete_row(self, row: tuple) -> None:
        await self.app.session.session.delete(self._table(*row))

    def __init__(self, session: api.Session, table: DeclarativeMeta, allow_add: bool = True, allow_delete: bool = True):
        super().__init__(
            show_row_labels=False, 
            fixed_rows=1 if allow_add else 0, 
            id=f"meta-table-display-{table.__tablename__}",
            cursor_type="row"
        )
        keys = self.add_columns(*table.columns.keys())
        self._map = dict(zip(table.columns.keys(), keys))
        self._conn = session.conn
        self._allow_delete = allow_delete
        self._allow_add = allow_add
        self._table = table

    def add_row(self, *cells, **kwargs):
        cells = list(cells)
        key = super().add_row(*cells, **kwargs)
        if self._allow_delete:
            cells.append(TableDisplayRowDeleteButton(key))
        super().add_row(*cells, **kwargs)
        


class TabPane(TabPane_):
    def __init__(self, session: api.Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = session


Tabs = list[tuple[str, TabPane]]
