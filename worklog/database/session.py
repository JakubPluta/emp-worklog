from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from worklog.config import settings
from worklog.database.utils import get_async_engine, get_async_session

SQLALCHEMY_DATABASE_URL = settings.resolve_database_url()

async_engine: AsyncEngine = get_async_engine(SQLALCHEMY_DATABASE_URL)
async_session: AsyncSession = get_async_session(SQLALCHEMY_DATABASE_URL)
