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

def test_bulk_add_items(client):
    bulk_data = {
        "items": [
            {"name": "Bulk Item 1", "price": 100.0},
            {"name": "Bulk Item 2", "price": 200.5},
            {"name": "Bulk Item 3", "price": 300.75}
        ]
    }

    response = client.post("/items/bulk", json=bulk_data)
    assert response.status_code == 201

    returned_items = response.json
    assert isinstance(returned_items, dict)

    created = returned_items.get("created", {})
    errors = returned_items.get("errors", {})

    assert len(created) == 3
    assert len(errors) == 0

    # Check that each item has a numeric id and matches input data
    for item_id, item in created.items():
        assert isinstance(int(item_id), int)
        assert "name" in item and "price" in item

    # Optionally, GET one of the added items by ID to confirm
    first_id = list(created.keys())[0]
    get_response = client.get(f"/item/{first_id}")
    assert get_response.status_code == 200
    assert get_response.json == created[first_id]
