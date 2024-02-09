"""
SQLAlchemy async engine and sessions tools

https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
"""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from worklog import config

from worklog.log import get_logger

log = get_logger(__name__)

def _resolve_db_uri(env: str) -> str:
    log.debug("Resolving database URI for environment %s", env)
    if env == "TEST":
        return config.settings.TEST_SQLALCHEMY_DATABASE_URI
    if env == "DEV" or env == "PROD":
        return config.settings.DEFAULT_SQLALCHEMY_DATABASE_URI
    raise ValueError("Invalid environment")


sqlalchemy_database_uri = _resolve_db_uri(config.settings.ENVIRONMENT)

async_engine = create_async_engine(sqlalchemy_database_uri, pool_pre_ping=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


