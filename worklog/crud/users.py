from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from worklog.models.users import User
from worklog.schemas.auth import UserRegister
from worklog.security import verify_password


async def get_user_by_id(session: AsyncSession, user_id: str) -> User | None:
    """
    Asynchronously retrieves a user by their ID using the provided session and user ID.

    Args:
        session (AsyncSession): The async session to use for the database query.
        user_id (str): The ID of the user to retrieve.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    results = await session.query(User).filter(User.id == user_id).first()
    return results


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """
    Asynchronously retrieves a user from the database based on the provided email.

    Args:
        session (AsyncSession): The async session to interact with the database.
        email (str): The email of the user to retrieve.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    results = await session.query(User).filter(User.email == email).first()
    return results


async def get_all_users(session: AsyncSession) -> List[User]:
    """
    Asynchronously retrieves all users from the database.

    Args:
        session (AsyncSession): The async session to interact with the database.

    Returns:
        list[User]: A list of user objects.
    """
    results = await session.query(User).all()
    return results


async def create_user(session: AsyncSession, user: UserRegister) -> User:
    """
    Asynchronously creates a new user in the database.

    Args:
        session (AsyncSession): The async session to interact with the database.
        user (User): The user object to create.

    Returns:
        User: The created user object.
    """
    user_create = user.model_dump(exclude_unset=True, exclude_none=True)
    user_to_db = User(**user_create)
    session.add(user_to_db)
    await session.commit()
    await session.refresh(user_to_db)
    return user_to_db

async def is_superuser(user: User) -> bool:
    return user.is_superuser

async def is_active(user: User) -> bool:
    return user.is_active

async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password):
        return None
    return user