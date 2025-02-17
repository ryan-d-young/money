import asyncio
from dataclasses import dataclass

import aiohttp

from src.api import core


class Daemon:
    def __init__(self):
        ...