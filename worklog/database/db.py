from contextlib import contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession

from worklog.database.session import async_session
from worklog.log import get_logger

log = get_logger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Asynchronous function that returns an async generator yielding an async database session."""
    log.debug("getting async database session")
    async with async_session() as session:
        yield session
    log.debug("closing async database session")


@contextmanager
async def get_ctx_db() -> Generator:
    """Context manager that creates an async database session and
    yields it for use in a 'with' statement."""
    async with async_session() as db_session:
        yield db_session
