import pytest
from app.app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"API is running" in rv.data

def test_post_and_get_item(client):
    # POST item 1
    response = client.post("/item/1", json={"name": "Test Item", "price": 10.5})
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Test Item"
    assert data["price"] == 10.5

    # GET item 1
    response = client.get("/item/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Test Item"

def test_put_item(client):
    # PUT (update) item 1
    response = client.put("/item/1", json={"name": "Updated Item", "price": 15.0})
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Updated Item"
    assert data["price"] == 15.0

def test_delete_item(client):
    # DELETE item 1
    response = client.delete("/item/1")
    assert response.status_code == 204

    # Confirm deletion
    response = client.get("/item/1")
    assert response.status_code == 404
