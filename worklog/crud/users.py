from typing import List
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from worklog.models.users import User
from worklog.schemas.auth import UserRegister
from worklog.security import verify_password
from worklog.log import get_logger

log = get_logger(__name__)

async def get_user_by_id(session: AsyncSession, user_id: str) -> User | None:
    """
    Asynchronously retrieves a user by their ID using the provided session and user ID.

    Args:
        session (AsyncSession): The async session to use for the database query.
        user_id (str): The ID of the user to retrieve.

    Returns:
        User | None: The user object if found, otherwise None.
    """
    log.debug("getting user with id=%s", user_id)
    results = await session.get(User, user_id)
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
    log.debug("getting user with email=%s", email)
    results = await session.execute(select(User).filter(User.email == email))
    user = results.scalars().first()
    return user


async def get_all_users(session: AsyncSession, offset: int, limit: int) -> List[User]:
    """
    Asynchronously retrieves all users from the database.

    Args:
        session (AsyncSession): The async session to interact with the database.

    Returns:
        list[User]: A list of user objects.
    """
    log.debug("getting all users with offset %s, limit: %s", offset,limit)
    stmt = select(User).offset(offset).limit(limit)
    results = await session.execute(stmt)
    return results.scalars().all()


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


async def delete_user(session: AsyncSession, user: User) -> User:
    """
    Asynchronous function to delete a user using the provided session and user object.
    
    Args:
        session (AsyncSession): The asynchronous session object for the database interaction.
        user (User): The user object to be deleted.
    
    Returns:
        User: The deleted user object.
    """
    log.debug("deleting user with %s", user.email)
    session.delete(user)
    await session.commit()
    return user
    
    
async def update_user(session):
    ...

async def is_superuser(user: User) -> bool:
    """
    Check if the user is a superuser.
    
    Args:
        user: The user object to check.
    
    Returns:
        bool: True if the user is a superuser, False otherwise.
    """
    return user.is_superuser

async def is_active(user: User) -> bool:
    """
    Check if the user is active.
    
    Args:
        user (User): The user object to check.

    Returns:
        bool: True if the user is active, False otherwise.
    """
    return user.is_active

async def authenticate_user(session: AsyncSession, email: str, password: str) -> User | None:
    """
    Asynchronously authenticates a user by verifying the provided email and password.

    Args:
        session (AsyncSession): The async session to interact with the database.
        email (str): The email of the user to authenticate.
        password (str): The password of the user to authenticate.

    Returns:
        User | None: The authenticated user if successful, otherwise None.
    """
    user = await get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password):
        return None
    return user