import time

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from worklog import config, security
from worklog.crud.users import get_user_by_email, get_user_by_id
from worklog.database import get_db
from worklog.models import User
from worklog.schemas.auth import AccessToken, JWTTokenPayload, RefreshToken
from worklog.schemas.users import UserCreate, UserInDB, UserOut

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

    user = await get_user_by_email(session, form_data.username)

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

    user = await get_user_by_id(session, token_data.sub)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return security.generate_access_token_response(str(user.id))



@router.post("/register", response_model=UserOut)
async def register_user(
    session: AsyncSession = Depends(get_db),
    user: UserCreate = Depends(),
):
    """
    An asynchronous function that registers a new user.

    Args:
        session (AsyncSession): The database session.
        user (UserCreate): The user data.

    Returns:
        UserOut: The created user.
    """
    u = get_user_by_email(session, user.email)
    if u:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    
    user_in = UserInDB(
        **user.model_dump(exclude_unset=True, exclude_defaults=True),
        hashed_password=security.get_password_hash(user.password),
    )
    await create_user(session, user_in)
    