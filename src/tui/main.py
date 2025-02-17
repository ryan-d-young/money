from typing import Any

from textual import work
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Button, Label, Select, Input, Footer
from textual.containers import Vertical, Horizontal
from textual.validation import Validator, ValidationResult

from src.api import api
from src.util import dt


COLS = [
    "id",          #  0: index
    "provider",    #  1: dropdown
    "router",      #  2: dropdown
    "collection",  #  3: dropdown
    "table",       #  4: dropdown
    "model",       #  5: dropdown
    "request",     #  6: dropdown
    "start",       #  7: datetime
    "end",         #  8: datetime
    "recurrence",  #  9: dropdown
    ""             # 10: button
]


class Delete(Button):
    def __init__(self, key: str):
        super().__init__(label="-", id=f"delete-button-{key}", variant="error")
        self.key = key

    def on_click(self) -> None:
        self.parent.remove_row(self.key)


class Display(DataTable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        keys = self.add_columns(*COLS)
        self._map = dict(zip(COLS, keys))

    def add_row(self, *cells, **kwargs):
        cells = list(cells)
        key = super().add_row(*cells, **kwargs)
        cells.append(Delete(key))
        super().add_row(*cells, **kwargs)


class DictSelector(Select):
    def __init__(self, name: str, **kwargs: dict[str, Any]):
        super().__init__(options=list(kwargs.keys()), prompt=name, id=f"selector-{name}")
        self._map = kwargs

    def value(self) -> str:
        return self._map[super().value]


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


class Main(App):
    _session: api.Session

    def __init__(self, session: api.Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = session

    def compose(self) -> ComposeResult:
        yield Display()
        yield Horizontal(
            Label(""),
            DictSelector("provider", **self._session.providers),
            DictSelector("router", **self._session.routers),
            DictSelector("collection", **self._session.collections),
            DictSelector("table", **self._session.tables),
            DictSelector("model", **self._session.models),
            DictSelector("request", **self._session.requests),
            DateTimeInput("start"),
            DateTimeInput("end"),
            DictSelector("recurrence", **self._session.recurrences),
        )
        yield Footer()
        