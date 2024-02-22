from uuid import uuid4
from worklog import security
from worklog.models import User
from worklog.schemas.auth import UserRegister
from worklog.schemas.users import UserCreate
from worklog.crud.users import users_crud
from sqlalchemy.ext.asyncio import AsyncSession
from worklog.log import get_logger
from typing import List, Dict

log = get_logger(__name__)

TEST_USER_ID = "f7bb15fa-0de1-4175-a677-c3cf2aef3ea8"
TEST_USER_NAME = "testuser"
TEST_USER_EMAIL = "testuser@testuser.com"
TEST_USER_PASSWORD = "testuser"

MOCKED_USERS = [
    {
        "id": str(uuid4()),  
        "name": f"testuser{i}", 
        "email": f"testuser{i}@testuser{i}.com",
        "password": "password",
        "is_active": True,
        "is_superuser": False
    } for i in range(10)
]


async def _create_user(
    session: AsyncSession,
    id: str = TEST_USER_ID,
    email: str = TEST_USER_EMAIL,
    name: str = TEST_USER_NAME,
    password: str = TEST_USER_PASSWORD,
    is_active: bool = True,
    is_superuser: bool = False,
) -> User:
    user = await users_crud.get_one_by_id(session, id)
    if user:
        log.debug("user with id %s already exists", id)
        return user
    user = User(
        id=id,
        email=email,
        name=name,
        hashed_password=security.get_password_hash(password),
        is_active=is_active,
        is_superuser=is_superuser,
    )

    return await users_crud._create_from_orm_object(session, user)



async def _create_many_users(session: AsyncSession, users: List[Dict] = MOCKED_USERS) -> List[User]:
    users_objects = [User(**{k: v for k, v in user.items() if k != "password"}, hashed_password=security.get_password_hash(user["password"])) for user in users]
    users = await users_crud._create_many_from_orm_objects(session, users_objects)
    return users

def _generate_jwt_token(user_id: str = TEST_USER_ID) -> str:
    return security.create_jwt_token(user_id, 60 * 60 * 24 * 30, refresh=False)[0]
