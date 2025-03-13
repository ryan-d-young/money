import asyncio
import multiprocessing as mp
from typing import Unpack

from src import api, util

from . import producer, daemon


async def run():
    ...


async def start(**kwargs: Unpack[util.settings.Settings]):
    settings = util.settings.Settings(**kwargs)
    ...
