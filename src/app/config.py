from src import util
from typing import TypedDict


class DaemonConfig(TypedDict):
    padding: float = 0.0


class ProducerConfig(TypedDict):
    interval: float = 1.0


class Config(TypedDict, total=False):
    host: str = "localhost"
    port: int = 8000
    daily_start: util.dt.time = util.dt.isonow()
    daily_end: util.dt.time = util.dt.isonow()
    daemon: DaemonConfig
    producer: ProducerConfig
