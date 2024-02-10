
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from worklog.models.users import User


async def get_user_by_id(
    session: AsyncSession, user_id: str
) -> User | None:
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