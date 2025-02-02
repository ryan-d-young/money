import asyncio
from dataclasses import dataclass, field
from collections import UserDict
from datetime import timedelta

from src.data.util import log


@dataclass(frozen=True)
class ScheduleItem:
    _id: int
    offset: timedelta = field(default_factory=lambda: timedelta(0))
    

class Schedule(UserDict):
    def __init__(self, *, items: list[ScheduleItem]):
        for item in items:
            ...
            

class Daemon:
    def __init__(self, schedule: Schedule):
        self.schedule = schedule

    async def start(self, env: dict[str, str]):
        ...