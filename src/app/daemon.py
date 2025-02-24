import asyncio
from logging import Logger

from src import api, util

from . import schedule


async def run(
    message_queue: asyncio.LifoQueue[api.core.Request],
    schedule: schedule.Schedule,
    logger: Logger,
    *,
    padding: float = 0.0,
):
    while True:
        try:
            current_request = next(schedule)
            logger.info(f"Sleeping until {current_request['start']}")
            await asyncio.sleep(current_request["start"] - util.dt.now() - padding)
            await message_queue.put(current_request)
            logger.info(f"Put request: {current_request}")
        except StopIteration:
            break
    logger.info("Shutting down")
