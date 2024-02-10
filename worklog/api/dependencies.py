import time
from typing import Tuple

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from worklog import config, security
from worklog.crud.users import get_user_by_id
from worklog.database import get_db
from worklog.models.users import User
from worklog.schemas.auth import JWTTokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/access-token")


async def get_pagination_offset_and_limit(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
) -> Tuple[int, int]:
    """
    Asynchronous function to get pagination offset and limit.

    Args:
        offset (int): The offset value, default is 0.
        limit (int): The limit value, default is 10.

    Returns:
        Tuple[int, int]: A tuple containing the offset and limit values.
    """
    return offset, limit


async def decode_and_validate_jwt_token(
    token: str = Depends(oauth2_scheme),
) -> JWTTokenPayload:
    """
    Asynchronously validates the token and returns the JWTTokenPayload.

    Args:
        token (str, optional): The token to be validated. Defaults to Depends(oauth2_scheme).

    Returns:
        JWTTokenPayload: The payload of the validated token.
    """

    try:
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[security.JWT_ALGORITHM]
        )
        token_data = JWTTokenPayload(**payload)

        if token_data.refresh:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials, cannot use refresh token",
            )

        current_time = int(time.time())
        if current_time < token_data.issued_at or current_time > token_data.expires_at:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials, token expired or not yet valid",
            )

        return token_data
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials.",
        )


async def get_current_user(
    session: AsyncSession = Depends(get_db),
    token: JWTTokenPayload = Depends(decode_and_validate_jwt_token),
) -> User:
    """
    Asynchronous function to retrieve the current user using the provided session and token.

    Parameters:
        session (AsyncSession): The asynchronous session object.
        token (str): The user's authentication token.

    Returns:
        User: The user object corresponding to the provided token.
    """

    user = await get_user_by_id(session, token.sub)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    A function to get the current active user.

    Args:
        current_user (User, optional): The current user. Defaults to Depends(get_current_user).

    Returns:
        User: The current active user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user."
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Asynchronously gets the current superuser.

    Args:
        current_user (User): The current user.

    Returns:
        User: The current superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
