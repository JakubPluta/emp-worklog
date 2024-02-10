from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from worklog.api import dependencies
from worklog.core.security import get_password_hash
from worklog.models import User
from worklog.schemas.requests import (UserCreateRequest,
                                      UserUpdatePasswordRequest)
from worklog.schemas.responses import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: User = Depends(dependencies.get_current_user),
):
    """Get current user"""
    return current_user


@router.delete("/me", status_code=204)
async def delete_current_user(
    current_user: User = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """Delete current user"""
    await session.execute(delete(User).where(User.id == current_user.id))
    await session.commit()


@router.post("/reset-password", response_model=UserResponse)
async def reset_current_user_password(
    user_update_password: UserUpdatePasswordRequest,
    session: AsyncSession = Depends(dependencies.get_session),
    current_user: User = Depends(dependencies.get_current_user),
):
    """Update current user password"""
    current_user.hashed_password = get_password_hash(user_update_password.password)
    session.add(current_user)
    await session.commit()
    return current_user


@router.post("/register", response_model=UserResponse)
async def register_new_user(
    new_user: UserCreateRequest,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """Create new user"""
    result = await session.execute(select(User).where(User.email == new_user.email))
    if result.scalars().first() is not None:
        raise HTTPException(status_code=400, detail="Cannot use this email address")
    user = User(
        email=new_user.email,
        hashed_password=get_password_hash(new_user.password),
    )
    session.add(user)
    await session.commit()
    return user
