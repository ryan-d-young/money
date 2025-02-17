import asyncio
from aiohttp import web
from .process import process


async def main() -> None:
    app = web.Application()
    app.add_routes([
        web.get("/", process),
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()
    