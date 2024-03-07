import pytest
from httpx import AsyncClient, codes
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils import MOCKED_USERS, TEST_USER_ID, TEST_USER_EMAIL, TEST_USER_NAME, TEST_USER_PASSWORD
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


@pytest.mark.parametrize(
    "offset, limit, status_code",
    [
        (0, 5, 200),
        (2, 5, 200),
        (5, 1, 200),
        (1, 0, 422),
    ],
)
async def test_read_all_users_with_pagination(
    client: AsyncClient, super_user_jwt_token, offset, limit, status_code
):
    response = await client.get(
        f"/users/?offset={offset}&limit={limit}", headers=super_user_jwt_token
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert len(response.json()) and len(response.json()) == limit


async def test_read_all_users_unauthorized(client: AsyncClient):
    response = await client.get("/users/")
    assert response.status_code == codes.UNAUTHORIZED


@pytest.mark.parametrize(
    "email, status_code",
    [
        *[(u["email"], 200) for u in MOCKED_USERS[:3]],
        ("notexist@testuser.com", 404),
    ],
)
async def test_read_user_by_eamil(
    client: AsyncClient, super_user_jwt_token, email: str, status_code: int
):
    response = await client.get(f"/users/email/{email}", headers=super_user_jwt_token)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "id, status_code",
    [
        *[(u["id"], 200) for u in MOCKED_USERS[:3]],
        ("notexist@testuser.com", 422),
        ("77ead757-c5af-4594-ae25-1596d482a12b", 404),
    ],
)
async def test_read_user_by_id(
    client: AsyncClient, super_user_jwt_token, id: str, status_code: int
):
    response = await client.get(f"/users/{id}", headers=super_user_jwt_token)
    assert response.status_code == status_code


async def test_can_create_user(client: AsyncClient, super_user_jwt_token):
    response = await client.post(
        "/users/",
        json={
            "name": "abc",
            "email": "abc@abc.com",
            "password": "abc",
        },
        headers=super_user_jwt_token,
    )
    data = response.json()
    assert response.status_code == 201
    
    user = await client.get(f"/users/{data['id']}", headers=super_user_jwt_token)
    assert user.json()['id'] == data['id']
    
async def test_cannot_create_user_if_email_exists(client: AsyncClient, super_user_jwt_token):
    response = await client.post(
        "/users/",
        json={
            "name": "zxc",
            "email": "zxc@zxc.com",
            "password": "zxc",
        },
        headers=super_user_jwt_token,
    )
    assert response.status_code == 201
    
    response = await client.post(
        "/users/",
        json={
            "name": "zxc",
            "email": "zxc@zxc.com",
            "password": "zxc",
        },
        headers=super_user_jwt_token,
    )
    assert response.status_code == 409
    
    
async def test_cannot_create_user_if_not_superuser(client: AsyncClient, active_user_jwt_token):
    response = await client.post(
        "/users/",
        json={
            "name": "zxc",
            "email": "zxc@zxc.com",
            "password": "zxc",
        },
        headers=active_user_jwt_token,
    )
    assert response.status_code == 403
    

async def test_can_update_user(client: AsyncClient, super_user_jwt_token):
    response = await client.patch(
        f"/users/{TEST_USER_ID}",
        json={
            "name": "newname",
            "password": "newpassword",
        },
        headers=super_user_jwt_token,
    )
    assert response.status_code == 200 
    assert response.json()["name"] == "newname"
    
    response = await client.get(
        f"/users/{TEST_USER_ID}",
        headers=super_user_jwt_token,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "newname" and response.json()["email"] == TEST_USER_EMAIL


async def test_cannot_update_user_if_not_superuser(client: AsyncClient, active_user_jwt_token):
    response = await client.patch(
        f"/users/{TEST_USER_ID}",
        json={
            "name": "newname",
            "password": "newpassword",
        },
        headers=active_user_jwt_token,
    )
    assert response.status_code == 403
    

async def test_can_update_myself(client: AsyncClient, active_user_jwt_token):
    response = await client.patch(
        f"/users/me",
        json={
            "name": "newname",
            "password": "newpassword",
        },
        headers=active_user_jwt_token,
    )
    assert response.status_code == 200 
    assert response.json()["name"] == "newname"
    
    response = await client.get(
        f"/users/me",
        headers=active_user_jwt_token,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "newname" and response.json()["email"] == TEST_USER_EMAIL
    
    
async def test_cannot_update_myself_if_not_authenticated(client: AsyncClient):
    response = await client.patch(
        f"/users/me",
        json={
            "name": "newname",
            "password": "newpassword",
        },
    )
    assert response.status_code == 401
    
    
async def test_can_delete_user(client: AsyncClient, super_user_jwt_token):
    response = await client.delete(
        f"/users/{TEST_USER_ID}",
        headers=super_user_jwt_token,
    )
    assert response.status_code == 204 
    
    response = await client.get(
        f"/users/{TEST_USER_ID}",
        headers=super_user_jwt_token,
    )
    assert response.status_code == 404
    

async def test_cannot_delete_user_if_not_superuser(client: AsyncClient, active_user_jwt_token):
    response = await client.delete(
        f"/users/{TEST_USER_ID}",
        headers=active_user_jwt_token,
    )
    assert response.status_code == 403