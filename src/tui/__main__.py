import asyncio

from src import api
from .main import Main


async def main() -> None:
    session = await api.connect()
    app = Main(session)
    await app.run_async()


if __name__ == "__main__":
    asyncio.run(main())
