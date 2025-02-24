import asyncio

from websockets.asyncio.server import serve

from src.api import connect, Session
from src.api.core import Request


async def handle_request(request: Request, session: Session):
    ...


async def handler(websocket):
    session = await connect()
    async for message in websocket:
        await handle_request(message, session)


async def main():
    async with serve(handler, "localhost", 8000) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
