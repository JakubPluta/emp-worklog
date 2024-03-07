from typing import List, Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from worklog.api.dependencies import (get_current_superuser, get_current_user,
                                      get_pagination_offset_and_limit)
from worklog.crud.users import UserCRUD, users_crud
from worklog.database.db import get_db
from worklog.models import User
from worklog.schemas.auth import AccessToken, JWTTokenPayload, RefreshToken
from worklog.schemas.users import (UserCreate, UserInDB, UserOut, UserUpdate,
                                   UserUpdateSelf)
from worklog.security import get_password_hash

users_crud: UserCRUD

router = APIRouter()


@router.get(
    "/me",
    response_model=UserOut,
    response_model_exclude=["is_active"],
    status_code=status.HTTP_200_OK,
)
async def read_current_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Retrieve the current user.

    Args:
        current_user (User, optional): The current user.
        Defaults to the value returned by get_current_user.

    Returns:
        User: The current user.
    """
    if current_user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )
    return current_user


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def read_user(
    user_id: UUID4,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> User:
    """
    Async function to retrieve a user by their ID.

    Args:
        user_id (UUID4): The unique identifier of the user.
        session (AsyncSession): The database session.

    Returns:
        User: The user object if found, raises an HTTPException with status code 404 if not found.
    """
    user = await users_crud.get_one_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/email/{email}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def read_user_by_email(
    email: str | EmailStr,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> User:
    """
    Async function to retrieve a user by their email address.

    Args:
        email (str | EmailStr): The email address of the user.
        session (AsyncSession): The database session.

    Returns:
        User: The user object if found, raises an HTTPException with status code 404 if not found.
    """
    user = await users_crud.get_user_by_email(session, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/", response_model=List[UserOut], status_code=status.HTTP_200_OK)
async def read_users(
    pagination: Tuple[int, int] = Depends(get_pagination_offset_and_limit),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
) -> list[User]:
    """
    A function to retrieve a list of users with pagination support.

    Args:
        pagination (Tuple[int, int]): A tuple containing the offset and limit for pagination.
        session (AsyncSession): An asynchronous session for interacting with the database.

    Returns:
        list[User]: A list of User objects.
    """
    offset, limit = pagination
    return await users_crud.get_many(session, offset=offset, limit=limit)


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    """
    Create a new user with the provided user data.
    Args:
        user_in (UserCreate): The user input data for creating a new user.
        session (AsyncSession, optional): The async session for database operations. Defaults to Depends(get_db).
    Returns:
        UserOut: The user data of the newly created user.
    """
    user = await users_crud.get_user_by_email(session, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    user = UserInDB(
        **user_in.model_dump(),
        hashed_password=get_password_hash(user_in.password),
    )
    try:
        user = await users_crud.create_user(session, user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
    return user


@router.patch("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
async def update_myself(
    user_in: UserUpdateSelf,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the current user's data.

    Args:
        user_in (UserCreate): The updated user data.
        session (AsyncSession, optional): The async session for database operations. Defaults to Depends(get_db).
        current_user (User, optional): The current user. Defaults to Depends(get_current_user).

    Returns:
        UserOut: The updated user data.
    """
    user = await users_crud.get_one_by_id(session, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user = await users_crud.update(session, user, user_in)
    return user

@router.patch("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: UUID4,
    user_in: UserUpdate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Update a user's data.

    Args:
        user_id (UUID4): The ID of the user to update.
        user_in (UserCreate): The updated user data.
        session (AsyncSession, optional): The async session for database operations. Defaults to Depends(get_db).

    Returns:
        UserOut: The updated user data.
    """
    user = await users_crud.get_one_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        user = await users_crud.update(session, user, user_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
    return user





@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID4,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_superuser),
):
    """
    Delete a user.

    Args:
        user_id (UUID4): The ID of the user to delete.
        session (AsyncSession, optional): The async session for database operations. Defaults to Depends(get_db).
        user (User, optional): The current user. Defaults to Depends(get_current_superuser).

    Returns:
        None
    """
    user = await users_crud.get_one_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await users_crud.delete(session, user)
