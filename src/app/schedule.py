import asyncio
from collections import UserList
from datetime import datetime, time
from typing import TypedDict, Unpack, Generator

from src.api import core


class ItemData(TypedDict, total=False):
    id: int
    provider: core.symbols.Provider
    router: core.symbols.Router
    collection: core.symbols.Collection | None
    request: dict
    time: time


class Item:
    def __init__(self, **data: Unpack[ItemData]):
        self.data = data
        self.created_at = datetime.now()
        self.completed_at = None
        self._lock = asyncio.Lock()

    async def __call__(self) -> ItemData:
        async with self._lock:
            if not self.completed_at:
                self.completed_at = datetime.now()
                return self.data
            else:
                raise RuntimeError("Item already completed")


class Schedule(UserList[Item]):
    @staticmethod
    def parse_record(record: dict) -> Generator[dict, None]:
        record["end"] = record["end"] or datetime.today().replace(hour=23, minute=59, second=59)
        recurrences = [record]
        while recurrences[-1]["end"] < record["end"]:
            i_n = record.copy()
            i_n["start"] += record["recurrence"]
            yield i_n

    @classmethod
    def from_orm(cls, schedule: list[dict]):
        data = []
        for record in schedule:
            for item in cls.parse_record(record):
                data.append(Item(**item))
        instance = cls(data)
        instance.sort()
        return instance

    def sort(self, **kwargs):
        super().sort(key=lambda x: x.data["start"])
