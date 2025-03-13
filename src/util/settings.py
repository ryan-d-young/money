from typing import TypedDict

from src import util


class Settings(TypedDict):
    server_host: str
    server_port: int
    server_poll_interval: float
    server_daemon_padding: float
    server_daily_start: util.dt.time
    server_daily_end: util.dt.time
