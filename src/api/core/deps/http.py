from asyncio import AbstractEventLoop
from typing import ClassVar

from httpx import AsyncClient

from . import dependency


class HttpClient(dependency.Dependency[AsyncClient]):
    instance: ClassVar[AsyncClient | None] = None
    name = "http"

    @classmethod
    async def start(cls, env: dict[str, str], loop: AbstractEventLoop):
        cls.instance = AsyncClient(verify=False)
        return cls

    @classmethod
    async def stop(cls, env: dict[str, str]):
        if cls.instance:
            await cls.instance.aclose()
            cls.instance = None
        return cls

    async def __aenter__(self) -> AsyncClient:
        if self.instance is None:
            raise RuntimeError("HttpClient not initialized")
        return self.instance

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass
