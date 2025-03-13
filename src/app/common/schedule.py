from collections import UserList
from datetime import datetime, time
from typing import TypedDict, Unpack, Generator

from src import util
from src.api import core


class ItemData(TypedDict):
    id: int
    provider: core.symbols.Provider
    router: core.symbols.Router
    request: core.request.Request
    t: time


class Item:
    id: int
    t: time
    request: core.request.Request

    def __init__(self, **data: Unpack[ItemData]):
        self.id = data.pop("id")
        self.t = data.pop("t")
        self.request = core.Request(**data)


class ItemGroup(UserList[Item]):
    t: time

    def __init__(self, t: time, *items: Item):
        super().__init__(items)
        self.t = t


class Schedule(UserList[Item]):
    def __init__(self, *items: Item):
        super().__init__(items)
        self._items = items

    @staticmethod
    def parse_record(record: dict) -> Generator[dict, None]:
        record_end = record["end"] or datetime.today().replace(hour=23, minute=59, second=59)
        record_time = record["start"]
        while record_time <= record_end:
            i_n = record.copy()
            i_n["time"] = record_time
            record_time += record["interval"]
            yield i_n

    @classmethod
    def from_orm(cls, schedule: list[dict]):
        data = []
        for record in schedule:
            for item in cls.parse_record(record):
                data.append(Item(**item))
        return cls(*sorted(data, key=lambda x: x.t))

    def next_group(self, duration: util.dt.timedelta = util.dt._1S) -> ItemGroup | None:
        group = None
        while item := self.pop(0):
            if group:
                if util.dt.within_duration(item.t, group.t, duration):
                    group.append(item)
            else:
                group = ItemGroup(item.t)
                group.append(item)
        return group
