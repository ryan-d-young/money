from sqlalchemy import MetaData, Table
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from .meta import metadata

SESSION_NOT_INITIALIZED = "Database session not initialized"


class OrmSessionMixin:
    """Mixin class for managing database session and metadata."""

    _session: AsyncSession | None = None

    @property
    def session(self) -> AsyncSession:
        """Get the current database session.

        Raises:
            ValueError: If database session is not initialized

        """
        if not self._session:
            raise ValueError(SESSION_NOT_INITIALIZED)
        return self._session

    async def init_db(
        self,
        dbengine: AsyncEngine,
        provider_metadata: list[MetaData],
    ) -> None:
        """Initialize the database connection and create tables."""
        async with dbengine.begin() as conn:
            await conn.run_sync(metadata.create_all)
            for md in provider_metadata:
                await conn.run_sync(md.create_all)
        self._session = AsyncSession(dbengine)

    async def stop_db(self, *, commit: bool = True) -> None:
        """Close the database session, optionally committing changes."""
        if commit:
            await self.session.commit()
        await self.session.close()

    async def load_metadata(self, md: MetaData) -> None:
        """Create tables for the given metadata."""
        await self.session.run_sync(md.create_all)

    def _table(self, table_name: str, md: MetaData) -> Table:
        """Get table by name from metadata."""
        return Table(table_name, md, autoload_with=self.session.bind)
