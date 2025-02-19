from textual.app import App, ComposeResult
from textual.widgets import RichLog, Footer
from textual.containers import Vertical
from sqlalchemy.ext.asyncio import AsyncSession
from src.api import api
from .content import Content


class Main(App):
    session: api.Session
    _richlog: RichLog

    def __init__(self, session: api.Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session
        self._richlog = RichLog(wrap=True, id="logger")
        session.logger.addHandler(lambda record: self._richlog.write(record.getMessage()))

    @property
    def db(self) -> AsyncSession:
        return self.session.session

    def compose(self) -> ComposeResult:
        with Vertical(id="main"):
            yield Content(self.session)
            yield self._richlog
            yield Footer()
        