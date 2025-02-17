from textual.containers import Vertical
from textual.widgets import TabPane, RichLog


class Status(Vertical):
    ...


class Home(TabPane):
    def __init__(self, logger: RichLog, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logger