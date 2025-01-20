from typing import Literal, AsyncGenerator

import yarl
import aiohttp
import pydantic
import sqlmodel

from src.money import core


class ClientSession(core.Dependency):
    _obj: aiohttp.ClientSession
    async def start(self):
        self._obj = aiohttp.ClientSession()
        self.started = True

    async def __aenter__(self, **kwargs) -> AsyncGenerator[aiohttp.ClientResponse, None]:
        async with self._obj as client:
            async with client.request(**kwargs) as response:
                yield response

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        return

    async def stop(self):
        await self._obj.close()
        self.started = False


class HTTPRequest(core.Request):
    url: str = pydantic.Field(...)
    method: Literal["get", "post", "put", "patch", "delete"] = pydantic.Field(default="get")
    params: pydantic.BaseModel | None = pydantic.Field(default=None)
    payload: pydantic.BaseModel | None = pydantic.Field(default=None)

    @pydantic.field_validator("url")
    @classmethod
    def validate_url(cls, url: str):
        try:
            _ = yarl.URL(url).build()
        except Exception as e:
            raise pydantic.ValidationError(f"Failed to parse URL: {url}") from e
