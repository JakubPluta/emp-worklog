from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from worklog.api import dependencies
from worklog.security import get_password_hash
from worklog.models import User
from worklog.schemas.auth import AccessToken, JWTTokenPayload, RefreshToken
from worklog.schemas.users import UserCreate, UserOut


router = APIRouter()


@router.get("/me", response_model=UserOut)
async def read_current_user(
    current_user: User = Depends(dependencies.get_current_user),
):
    return current_user


