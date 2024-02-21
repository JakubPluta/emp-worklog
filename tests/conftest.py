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


def _get_testuser_obj(is_active=True, is_superuser=False) -> User:
    return User(
        id="f7bb15fa-0de1-4175-a677-c3cf2aef3ea8",
        name='testuser',
        email="testuser@testuser.com",
        hashed_password=security.get_password_hash("testuser"),
        is_active=is_active,
        is_superuser=is_superuser,
    )

def _get_test_jwt(user_id: str) -> str:
    return security.create_jwt_token(user_id, 60 * 60 * 24 * 30, refresh=False)[0]


@pytest_asyncio.fixture
async def active_test_user():
    return _get_testuser_obj()

@pytest_asyncio.fixture
async def inactive_test_user():
    return _get_testuser_obj(is_active=False)

@pytest_asyncio.fixture
async def superuser_test_user():
    return _get_testuser_obj(is_active=True, is_superuser=True)


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
async def default_user(test_db_setup, active_test_user) -> User:
    print("Creating test user")
    print(active_test_user)
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == active_test_user.email)
        )
        user = result.scalars().first()
        print(user)
        if user is None:
            new_user = active_test_user
            print(new_user)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user
        return user
    
@pytest_asyncio.fixture
async def test_user_access_token(default_user: User) -> str:
    jwt = _get_test_jwt(default_user.id)
    return jwt


@pytest_asyncio.fixture
async def valid_jwt_token(test_user_access_token: str):
    return {"Authorization": f"Bearer {test_user_access_token}"}
