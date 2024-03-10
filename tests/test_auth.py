from httpx import AsyncClient, codes

from worklog.main import app
from worklog.models import User


async def test_should_login_for_access_token(
    client: AsyncClient, active_user_jwt_token
):
    response = await client.post(
        "/auth/access-token",
        data={"username": "testuser@testuser.com", "password": "testuser"},
    )
    assert response.status_code == codes.OK
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "Bearer"


async def test_should_not_login_for_access_token_if_invalid_password(
    client: AsyncClient, active_user_jwt_token
):
    response = await client.post(
        "/auth/access-token",
        data={"username": "testuser@testuser.com", "password": "testuser1"},
    )
    assert response.json()["detail"] == "Incorrect email or password"
    assert response.status_code == 400


