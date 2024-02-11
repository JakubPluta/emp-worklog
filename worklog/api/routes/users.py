from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from worklog.api.dependencies import get_pagination_offset_and_limit, get_current_user
from worklog.crud import users as users_crud
from worklog.security import get_password_hash
from worklog.models import User
from worklog.schemas.auth import AccessToken, JWTTokenPayload, RefreshToken
from worklog.schemas.users import UserCreate, UserOut
from worklog.database.db import get_db

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.get("/{user_id}", response_model=UserOut)
async def read_user(
    user_id: str,
    session: AsyncSession = Depends(get_db),
) -> User:
    user = await users_crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/", response_model=list[UserOut])
async def read_users(
    offset: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
) -> list[User]:
    users = await users_crud.get_all_users(session, offset, limit)
    return users


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_db),
):
    user = await users_crud.get_user_by_email(session, user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    await users_crud.create_user(session, user)
    
