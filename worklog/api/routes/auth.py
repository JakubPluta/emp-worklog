import time

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from worklog.crud.users import users_crud
from worklog import config, security
from worklog.database import get_db
from worklog.models import User
from worklog.schemas.auth import AccessToken, JWTTokenPayload, RefreshToken, UserRegister
from worklog.schemas.users import UserCreate, UserInDB, UserOut, UserUpdate, UserUpdatePassowrd

from worklog.api.dependencies import get_current_user
router = APIRouter()


@router.post("/access-token", response_model=AccessToken)
async def login_for_access_token(
    session: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    An asynchronous function that handles the login process to obtain an access token.
    
    Args:
        session (AsyncSession): The database session.
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
        
    Returns:
        AccessToken: The access token response.
    """

    user = await users_crud.get_user_by_email(session, form_data.username)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    return security.generate_access_token_response(str(user.id))


@router.post("/refresh-token", response_model=AccessToken)
async def refresh_token(
    input: RefreshToken,
    session: AsyncSession = Depends(get_db),
):
    """
    Refreshes the access token using the refresh token. 
    Validates the refresh token and generates a new access token.
    
    Args:
        input (RefreshToken): The refresh token input.
        session (AsyncSession, optional): The async session for database access. Defaults to Depends(get_db).

    Returns:
        AccessToken: The new access token.
    """

    try:
        payload = jwt.decode(
            input.refresh_token,
            config.settings.SECRET_KEY,
            algorithms=[security.JWT_ALGORITHM],
        )
    except (jwt.DecodeError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials, unknown error",
        )

    token_data = JWTTokenPayload(**payload)

    if not token_data.refresh:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials, cannot use access token",
        )
    now = int(time.time())
    if now < token_data.issued_at or now > token_data.expires_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials, token expired or not yet valid",
        )

    user = await users_crud.get_user_by_id(session, token_data.sub)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return security.generate_access_token_response(str(user.id))



@router.post("/reset-password", response_model=UserOut)
async def reset_current_user_password(
    user_update_password: UserUpdatePassowrd,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reset the current user's password.

    Args:
        user_update_password (UserUpdatePassowrd): The updated password for the user.
        session (AsyncSession, optional): The async session for the database. Defaults to Depends(get_db).
        current_user (User, optional): The current user. Defaults to Depends(get_current_user).

    Returns:
        User: The current user with the updated password.
    """

    current_user.hashed_password = security.get_password_hash(user_update_password.password)
    session.add(current_user)
    await session.commit()
    return current_user


@router.post("/register", response_model=UserOut)
async def register_new_user(
    new_user: UserRegister,
    session: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    Args:
        new_user (UserRegister): The user to register.
        session (AsyncSession, optional): The database session.

    Returns:
        UserOut: The registered user.
    """

    user = await users_crud.get_user_by_email(session, new_user.email)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot use this email address")
    user = UserInDB(**new_user.dict())
    await users_crud.create_user(session, user)
    return user