from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection, AsyncTransaction, AsyncEngine
from typing import AsyncGenerator


class AsyncDatabaseManager:
    engine: AsyncEngine
    def __init__(
        self,     
        host: str, port: int, 
        user: str, pswd: str, 
        protocol: str = "postgresql", 
        dialect: str = "asyncpg",
        **kwargs
    ):
        self.engine = create_async_engine(
            url=f"{protocol}+{dialect}://{user}:{pswd}@{host}:{port}", 
            **kwargs
        )

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncTransaction, None]:
        async with self.engine.connect() as conn:
            async with conn.begin() as transaction:
                yield transaction

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[AsyncConnection, None]:
        async with self.engine.connect() as conn:
            yield conn