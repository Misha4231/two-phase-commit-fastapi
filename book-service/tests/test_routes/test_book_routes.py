import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_route_create_book(client: AsyncClient):
    new_book_data = {"title": "Dune", "author": "Frank Herbert", "stock": 10, "price": 29.99}
    response = await client.post("/books/", json=new_book_data)
    data = response.json()
    assert response.status_code == 201
    assert data["title"] == new_book_data["title"]
    assert data["author"] == new_book_data["author"]
    assert data["stock"] == new_book_data["stock"]
    assert float(data["price"]) == new_book_data["price"]
    assert "id" in data


@pytest.mark.anyio
async def test_route_list_all_books(client: AsyncClient):
    new_book_data = {"title": "Dune", "author": "Frank Herbert", "stock": 10, "price": 29.99}
    await client.post("/books/", json=new_book_data)
    response = await client.get("/books/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["title"] == new_book_data["title"]
    assert data[0]["author"] == new_book_data["author"]
    assert data[0]["stock"] == new_book_data["stock"]
    assert float(data[0]["price"]) == new_book_data["price"]
    assert "id" in data[0]
    assert "created_at" in data[0]
    assert "updated_at" in data[0]


@pytest.mark.anyio
async def test_route_get_book_by_id(client: AsyncClient):
    new_book_data = {"title": "1984", "author": "George Orwell", "stock": 5, "price": 14.99}
    create_response = await client.post("/books/", json=new_book_data)
    new_book = create_response.json()
    response = await client.get(f"/books/{new_book['id']}")
    data = response.json()
    assert response.status_code == 200
    assert data["title"] == new_book_data["title"]
    assert data["author"] == new_book_data["author"]
    assert data["stock"] == new_book_data["stock"]
    assert float(data["price"]) == new_book_data["price"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.anyio
async def test_route_get_book_by_id_not_found(client: AsyncClient):
    response = await client.get("/books/999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_update_book(client: AsyncClient):
    new_book_data = {"title": "Old Title", "author": "Old Author", "stock": 3, "price": 9.99}
    create_response = await client.post("/books/", json=new_book_data)
    new_book = create_response.json()
    response = await client.put(
        f"/books/{new_book['id']}",
        json={"title": "New Title", "author": "New Author", "stock": 99, "price": 49.99},
    )
    data = response.json()
    assert response.status_code == 200
    assert data["title"] == "New Title"
    assert data["author"] == "New Author"
    assert data["stock"] == 99
    assert float(data["price"]) == 49.99


@pytest.mark.anyio
async def test_update_book_not_found(client: AsyncClient):
    response = await client.put("/books/999", json={"title": "x"})
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_book(client: AsyncClient):
    new_book_data = {"title": "Dune", "author": "Frank Herbert", "stock": 10, "price": 29.99}
    create_response = await client.post("/books/", json=new_book_data)
    new_book = create_response.json()
    response = await client.delete(f"/books/{new_book['id']}")
    assert response.status_code == 204
    # ensure it's gone
    response = await client.get(f"/books/{new_book['id']}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_book_not_found(client: AsyncClient):
    response = await client.delete("/books/999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_book_invalid_payload(client: AsyncClient):
    # missing required fields
    response = await client.post("/books/", json={"title": "Only Title"})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_create_book_invalid_types(client: AsyncClient):
    response = await client.post(
        "/books/", json={"title": 123, "author": "Author", "stock": "not-an-int", "price": "free"}
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_update_partial_title(client: AsyncClient):
    new_book_data = {"title": "Original", "author": "Author", "stock": 5, "price": 9.99}
    create_response = await client.post("/books/", json=new_book_data)
    new_book = create_response.json()
    response = await client.put(f"/books/{new_book['id']}", json={"title": "Updated Title"})
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Author"
    assert data["stock"] == 5
    assert float(data["price"]) == 9.99


@pytest.mark.anyio
async def test_update_partial_stock(client: AsyncClient):
    new_book_data = {"title": "Title", "author": "Author", "stock": 5, "price": 9.99}
    create_response = await client.post("/books/", json=new_book_data)
    new_book = create_response.json()
    response = await client.put(f"/books/{new_book['id']}", json={"stock": 50})
    data = response.json()
    assert data["title"] == "Title"
    assert data["stock"] == 50
    assert float(data["price"]) == 9.99
