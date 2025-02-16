from typing import TypedDict
from enum import Enum, auto
from datetime import datetime

from src.api import core


class Item(core.Record):
    provider: str
    active: bool
    start: datetime
    


class Schedule(UserList[Item]):
    def __init__(self, *items: Item):
        ...
    