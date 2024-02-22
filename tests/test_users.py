from httpx import AsyncClient, codes
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from worklog.main import app
from worklog.models import User


async def test_read_current_user(client: AsyncClient, active_user_jwt_token):
    response = await client.get("/users/me", headers=active_user_jwt_token)
    assert response.status_code == codes.OK
    assert response.json() == {
        "email": "testuser@testuser.com",
        "name": "testuser",
        "id": "f7bb15fa-0de1-4175-a677-c3cf2aef3ea8",
    }

async def test_read_current_user_unauthorized(client: AsyncClient):
    response = await client.get("/users/me")
    assert response.status_code == codes.UNAUTHORIZED

async def test_read_current_user_inactive(client: AsyncClient, inactive_user_jwt_token):
    response = await client.get("/users/me", headers=inactive_user_jwt_token)
    assert response.status_code == codes.UNAUTHORIZED
    

async def test_read_all_users(client: AsyncClient, super_user_jwt_token, many_users):
    response = await client.get("/users/", headers=super_user_jwt_token)
    assert response.status_code == codes.OK
    assert len(response.json()) == len(many_users)
    
    