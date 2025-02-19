from typing import Any

from sqlalchemy.orm import DeclarativeMeta
from textual import work
from textual.validation import ValidationResult, Validator
from textual.widgets import Button, DataTable, Input, Select, ListItem, Label, TabPane as TabPane_
from textual.app import ComposeResult
from src import api, util


class DateTimeInput(Input):

    class DateTimeValidator(Validator):
        def validate(self, value: str) -> ValidationResult:
            try:
                util.dt.convert(d_str=value)
            except ValueError:
                return self.failure("Invalid date/time")
            return self.success()

    def __init__(self, name: str):
        super().__init__(
            placeholder=util.dt._ISODATE,
            validators=(self.DateTimeValidator(),),
            id=f"datetime-input-{name}",
        )


class DictSelector(Select):
    def __init__(self, name: str, data: dict[str, Any], *args, **kwargs):
        super().__init__(
            options=list(data.keys()), 
            prompt=name, 
            id=f"selector-{name}", 
            *args, **kwargs
        )
        self._map = data

    def value(self) -> str:
        return self._map[super().value]


class TableDisplayRowDeleteButton(Button):
    def __init__(self, key: str, *args, **kwargs):
        super().__init__(
            label="-", 
            id=f"delete-button-{key}", 
            variant="error", 
            *args, **kwargs
        )
        self.key = key

    def on_click(self) -> None:
        self.parent.remove_row(self.key)
        self.parent.delete_row(
            row=self.parent._table(
                *self.parent.get_row(self.key)
            )
        )


class RowListView(ListItem):
    def __init__(self, key: str, data: tuple[Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = key
        self.data = {item: Label(item) for item in data}
        
    def compose(self) -> ComposeResult:
        for value in self.data.values():
            yield value

    def pop(self, key: str) -> None:
        self.data.pop(key)

    def insert(self, value: str) -> None:
        self.data[value] = Label(value)


class TableDisplay(DataTable):
    @work
    async def load_table(self) -> list[tuple]:
        return await self.app.db.refresh(self._table)

    @work
    async def insert_row(self, row: tuple) -> None:
        await self.app.db.add(self._table(*row))

    @work
    async def update_row(self, row: tuple) -> None:
        await self.app.db.merge(self._table(*row))

    @work
    async def delete_row(self, row: tuple) -> None:
        await self.app.db.delete(self._table(*row))

    @work
    async def delete_index(self, index: int) -> None:
        await self.app.db.delete(self._table.get_row(index))

    def __init__(
        self, 
        table: DeclarativeMeta, 
        allow_add: bool = True, 
        allow_delete: bool = True, 
        *args, **kwargs
    ):
        super().__init__(
            show_row_labels=False, 
            fixed_rows=1 if allow_add else 0, 
            cursor_type="row",
            *args, **kwargs
        )
        keys = self.add_columns(*table.columns.keys())
        self._map = dict(zip(table.columns.keys(), keys))
        self._allow_delete = allow_delete
        self._allow_add = allow_add
        self._table = table

    def add_row(self, *cells, **kwargs):
        if self._allow_add:
            cells = list(cells)
            key = super().add_row(*cells, **kwargs)
            if self._allow_delete:
                cells.append(TableDisplayRowDeleteButton(key))
            super().add_row(*cells, **kwargs)
            cells.pop()
            self.insert_row(cells)

    def remove_row(self, key: str) -> None:
        if self._allow_delete:
            super().remove_row(key)
            self.delete_index(key)


class TabPane(TabPane_):
    def __init__(self, session: api.Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = session


Tabs = list[tuple[str, TabPane]]
