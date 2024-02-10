from sqlalchemy.ext.asyncio import (AsyncEngine, async_sessionmaker,
                                    create_async_engine)


def get_async_engine(database_url: str, echo=False, pool_pre_ping=True) -> AsyncEngine:
    """
    Creates an asynchronous engine for the given database URL.

    Args:
        database_url (str): The URL of the database.
        echo (bool, optional): Whether to enable logging. Defaults to False.
        pool_pre_ping (bool, optional): Whether to ping the database before creating the engine.
            Defaults to True.

    Returns:
        AsyncEngine: The asynchronous engine created.
    """

    engine = create_async_engine(database_url, echo=echo, pool_pre_ping=pool_pre_ping)
    return engine


def get_async_session(
    database_url: str, echo=False, pool_pre_ping=True, expire_on_commit=False
) -> async_sessionmaker[AsyncEngine]:
    """
    Creates an asynchronous session for the given database URL.

    Args:
        database_url (str): The URL of the database.
        echo (bool, optional): Whether to enable logging. Defaults to False.
        pool_pre_ping (bool, optional): Whether to ping the database before creating the engine.
            Defaults to True.
        expire_on_commit (bool, optional): Whether to expire the session on commit. Defaults to False.

    Returns:
        async_sessionmaker[AsyncEngine]: The asynchronous session created.
    """

    engine = get_async_engine(database_url, echo=echo, pool_pre_ping=pool_pre_ping)
    async_session = async_sessionmaker(engine, expire_on_commit=expire_on_commit)
    return async_session
