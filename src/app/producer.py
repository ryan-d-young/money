import asyncio

from src import api


async def run(session: api.Session, message_queue: asyncio.LifoQueue[api.core.Request], *, interval: float = 0.25) -> asyncio.LifoQueue[api.core.Request]:
    ...
