import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_user(client: AsyncClient):
    new_user_data = {"name": "test", "balance": 100}

    response = await client.post(
        "/users/",
        json=new_user_data
    )

    data = response.json()

    assert response.status_code == 201
    assert data["name"] == new_user_data["name"]
    assert data["balance"] == new_user_data["balance"]
    assert "id" in data