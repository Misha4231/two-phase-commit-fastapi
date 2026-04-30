import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_route_create_user(client: AsyncClient):
    new_user_data = {"name": "test", "balance": 100}

    response = await client.post("/users/", json=new_user_data)
    data = response.json()

    assert response.status_code == 201
    assert data["name"] == new_user_data["name"]
    assert data["balance"] == new_user_data["balance"]
    assert "id" in data


@pytest.mark.anyio
async def test_route_list_all_users(client: AsyncClient):
    new_user_data = {"name": "test1", "balance": 101}

    await client.post("/users/", json=new_user_data)
    response = await client.get("/users/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["name"] == new_user_data["name"]
    assert data[0]["balance"] == new_user_data["balance"]
    assert "id" in data[0]
    assert "created_at" in data[0]
    assert "updated_at" in data[0]


@pytest.mark.anyio
async def test_route_get_user_by_id(client: AsyncClient):
    new_user_data = {"name": "test2", "balance": 141}

    create_response = await client.post("/users/", json=new_user_data)
    new_user = create_response.json()

    response = await client.get(f"/users/{new_user['id']}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == new_user_data["name"]
    assert data["balance"] == new_user_data["balance"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_route_get_user_by_id_not_found(client: AsyncClient):
    response = await client.get(f"/users/999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_update_user(client: AsyncClient):
    new_user_data = {"name": "test2", "balance": 141}

    create_response = await client.post("/users/", json=new_user_data)
    new_user = create_response.json()

    response = await client.put(
        f"/users/{new_user['id']}", json={"name": "updated", "balance": 20}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "updated"
    assert data["balance"] == 20


@pytest.mark.anyio
async def test_update_user_not_found(client: AsyncClient):
    response = await client.put("/users/999", json={"name": "x"})

    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_user(client: AsyncClient):
    new_user_data = {"name": "test2", "balance": 141}

    create_response = await client.post("/users/", json=new_user_data)
    new_user = create_response.json()

    response = await client.delete(f"/users/{new_user['id']}")

    assert response.status_code == 204

    # ensure it's gone
    response = await client.get(f"/users/{new_user['id']}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_user_not_found(client: AsyncClient):
    response = await client.delete("/users/999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_user_invalid_payload(client: AsyncClient):
    response = await client.post("/users/", json={"name": 123, "balance": "invalid"})

    assert response.status_code == 422


@pytest.mark.anyio
async def test_update_partial(client: AsyncClient):
    new_user_data = {"name": "test2", "balance": 141}

    create_response = await client.post("/users/", json=new_user_data)
    new_user = create_response.json()

    response = await client.put(f"/users/{new_user['id']}", json={"name": "only_name"})

    data = response.json()

    assert data["name"] == "only_name"
    assert data["balance"] == 141
