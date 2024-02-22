import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from worklog import config, security
from worklog.database.session import async_engine, async_session
from worklog.main import app
from worklog.models import Base, User
from tests.utils import _create_many_users, _create_user, _generate_jwt_token

@pytest_asyncio.fixture
async def many_users(session):
    users = await _create_many_users(session)
    return users


@pytest_asyncio.fixture
async def active_test_user(session):
    user =  await _create_user(session)
    return user

@pytest_asyncio.fixture
async def inactive_test_user(session):
    user = await _create_user(session, is_active=False)
    return user

@pytest_asyncio.fixture
async def superuser_test_user(session):
    user = await _create_user(session, is_superuser=True)
    return user

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_db_setup():
    assert config.settings.ENVIRONMENT == "TEST"

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)



@pytest_asyncio.fixture(autouse=True)
async def session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

        for _, table in Base.metadata.tables.items():
            await session.execute(delete(table))
        await session.commit()


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        client.headers.update({"Host": "localhost"})
        yield client


@pytest_asyncio.fixture
async def active_user_jwt_token(active_test_user):
    return {"Authorization": f"Bearer {_generate_jwt_token(active_test_user.id)}"}

@pytest_asyncio.fixture
async def inactive_user_jwt_token(inactive_test_user):
    return {"Authorization": f"Bearer {_generate_jwt_token(inactive_test_user.id)}"}

@pytest_asyncio.fixture
async def super_user_jwt_token(superuser_test_user):
    return {"Authorization": f"Bearer {_generate_jwt_token(superuser_test_user.id)}"}