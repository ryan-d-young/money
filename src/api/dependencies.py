import aiohttp
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.util import env
from .core.dependency import Dependency


class ClientSession(Dependency[aiohttp.ClientSession]):
    @classmethod
    async def start(cls, env: dict[str, str]):
        cls._instance = aiohttp.ClientSession()
        return cls

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls._instance.close()
        cls._instance = None
        

class DBEngine(Dependency[AsyncEngine]):
    @classmethod
    async def start(cls, env: dict[str, str]):
        url = (
            f"postgresql+asyncpg://"
            f"{env['DBUSER']}:{env['DBPASS']}@"
            f"{env['DBHOST']}:{env['DBPORT']}"
        )
        cls._instance = create_async_engine(url)

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls._instance.dispose()
        cls._instance = None
        return cls


class DependencyManager:
    def __init__(self, *dependencies: Dependency):
        self.dependencies = {}
        for dependency in dependencies:
            self.dependencies[dependency.__name__.lower()] = dependency

    async def start(self):
        env_ = env.load()
        for dependency in self.dependencies.values():
            await dependency.start(env_)

    def get(self, name: str) -> Dependency:
        return self.dependencies[name]._instance

    async def stop(self):
        env_ = env.load()
        for dependency in self.dependencies.values():
            await dependency.stop(env_)
