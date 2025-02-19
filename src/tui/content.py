from textual.app import ComposeResult
from textual.widgets import Tab
from textual.containers import Container

from src import api
from .tabs import tabs


class Content(Container):
    def __init__(self, session: api.Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session

    def compose(self) -> ComposeResult:
        for name, tab in tabs:
            with Tab(name, id=f"tab-{name}"):
                yield tab(self.session)
