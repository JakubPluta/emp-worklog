from httpx import AsyncClient, codes
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from worklog.main import app
from worklog.models import User

async def test_read_current_user(client: AsyncClient, valid_jwt_token):
    response = await client.get("/users/me", headers=valid_jwt_token)
    assert response.status_code == codes.OK
    assert response.json() == {'email': 'testuser@testuser.com', 'name': 'testuser', 'id': 'f7bb15fa-0de1-4175-a677-c3cf2aef3ea8'}