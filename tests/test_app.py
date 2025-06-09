import pytest
from app.app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json == {"message": "API is running"}

def test_post_and_get_item(client):
    # Post an item
    response = client.post("/item/1", json={"name": "Test Item", "price": 10.5})
    assert response.status_code == 201
    assert response.json == {"name": "Test Item", "price": 10.5}

    # Get the same item
    response = client.get("/item/1")
    assert response.status_code == 200
    assert response.json == {"name": "Test Item", "price": 10.5}

def test_put_item(client):
    # Put (create or update) an item
    response = client.put("/item/2", json={"name": "Another Item", "price": 20.0})
    assert response.status_code == 200
    assert response.json == {"name": "Another Item", "price": 20.0}

def test_patch_item(client):
    client.post("/item/3", json={"name": "Patch Item", "price": 15.0})

    # Patch item name only
    response = client.patch("/item/3", json={"name": "Patched Name"})
    assert response.status_code == 200
    assert response.json["name"] == "Patched Name"
    assert response.json["price"] == 15.0

def test_delete_item(client):
    client.post("/item/4", json={"name": "Delete Item", "price": 5.0})

    # Delete the item
    response = client.delete("/item/4")
    assert response.status_code == 204

    # Confirm deletion
    response = client.get("/item/4")
    assert response.status_code == 404
