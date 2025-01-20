import asyncio
from logging import Logger
from enum import Enum, auto

from src.money import core
from . import logger


class Stage(Enum):
    INIT_ROUTERS = auto()
    INIT_DEPS = auto()
    PLAN_EXECUTION = auto()
    


class State:
    queue: asyncio.PriorityQueue
    logger: Logger
    dependencies: list[core.Dependencu]
    def __init__(self):
        self.queue = asyncio.PriorityQueue()
        self.logger = logger.init("server")
        self.dependencies = []
        self.stage = Stage.INIT_ROUTERS
        