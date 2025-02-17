from src.api import api
from .common import DateTimeInput, DictSelector, TableDisplay, TabPane

COLS = [
    "id",  #  0: index
    "provider",  #  1: dropdown
    "router",  #  2: dropdown
    "collection",  #  3: dropdown
    "table",  #  4: dropdown
    "model",  #  5: dropdown
    "request",  #  6: dropdown
    "start",  #  7: datetime
    "end",  #  8: datetime
    "recurrence",  #  9: dropdown
    "",  # 10: button
]


class Schedule(TabPane):
    def __init__(self, session: api.Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session
