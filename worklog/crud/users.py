from typing import List

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from worklog.crud.base import CRUDRepository
from worklog.log import get_logger
from worklog.models.users import User
from worklog.schemas.auth import UserRegister
from worklog.security import verify_password

log = get_logger(__name__)


class UserCRUD(CRUDRepository):
    async def get_user_by_email(self, session: AsyncSession, email: str) -> User | None:
        """
        Asynchronously retrieves a user from the database based on the provided email.

        Args:
            session (AsyncSession): The async session to interact with the database.
            email (str): The email of the user to retrieve.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        log.debug("getting user with email=%s", email)
        results = await session.execute(select(User).where(User.email == email))
        return results.scalars().first()

    async def is_superuser(self, session: AsyncSession, email: str) -> bool:
        """
        Asynchronously checks if a user is a superuser.

        Args:
            session (AsyncSession): The async session to interact with the database.
            email (str): The email of the user to check.

        Returns:
            bool: True if the user is a superuser, False otherwise.
        """
        user = await self.get_user_by_email(session, email)
        if not user:
            return False
        return user.is_superuser

    async def is_active_user(self, session: AsyncSession, email: str) -> bool:
        """
        Asynchronously checks if a user is active.

        Args:
            session (AsyncSession): The async session to interact with the database.
            email (str): The email of the user to check.

        Returns:
            bool: True if the user is active, False otherwise.
        """
        user = await self.get_user_by_email(session, email)
        if not user:
            return False
        return user.is_active

    async def create_user(self, session: AsyncSession, user: UserRegister) -> User:
        """
        Asynchronously creates a new user in the database.

        Args:
            session (AsyncSession): The async session to interact with the database.
            user (UserRegister): The user object to create.

        Returns:
            User: The created user object.
        """
        user_create = user.model_dump(exclude_unset=True, exclude_none=True)
        user_to_db = User(**user_create)
        session.add(user_to_db)
        await session.commit()
        await session.refresh(user_to_db)
        return user_to_db

    async def authenticate_user(
        self, session: AsyncSession, email: str, password: str
    ) -> User | None:
        """
        Asynchronously authenticates a user by verifying the provided email and password.

        Args:
            session (AsyncSession): The async session to interact with the database.
            email (str): The email of the user to authenticate.
            password (str): The password of the user to authenticate.

        Returns:
            User | None: The authenticated user if successful, otherwise None.
        """
        user = await self.get_user_by_email(session, email)
        if not user:
            return None
        if not verify_password(password):
            return None
        return user


users_crud = UserCRUD(User)
