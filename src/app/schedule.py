from collections import UserList
from datetime import datetime, timedelta, time
from typing import TypedDict, Unpack

from sqlalchemy.orm import DeclarativeMeta
from pydantic import BaseModel

from src.api import core


class ItemData(TypedDict):
    id: int
    provider: core.Provider
    table: DeclarativeMeta | None
    model: BaseModel | None
    collection: core.Collection | None
    request: dict
    time: time


class Item:
    def __init__(self, **data: Unpack[ItemData]):
        self.data = data
        self.created_at = datetime.now()
        self.completed_at = None

    def __call__(self) -> ItemData:
        if not self.completed_at:
            self.completed_at = datetime.now()
            return self.data
        else:
            raise RuntimeError("Item already completed")


class Schedule(UserList[Item]):
    @staticmethod
    def parse_orm_item(item: core.Schedule) -> list[Item]:
        ...
    
    def __init__(self, *items: Item):
        super().__init__(items)
        self.sort(key=lambda x: x["start"])

        for item in self:
            item["end"] = item["end"] or datetime.today().replace(hour=23, minute=59, second=59)
            recurrences = [item]

            while recurrences[-1]["end"] < item["end"]:
                item_copy = item.copy()
                item_copy["start"] += item["recurrence"]
                ...
        