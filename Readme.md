## Simple Flask API Demo With Nginx Reverse Proxy 

### Features
* In-Memory Storage: Uses a dictionary for simplicity (AWS Free Tier compatible, no database needed).
* Request Validation: Uses reqparse to enforce required fields (name, price).
* Error Handling: Returns appropriate HTTP status codes (e.g., 404 for not found, 400 for bad requests).
* Nginx Integration: The API listens on port 5000 which is processed by Nginx reverse proxy 

### Endpoints
* GET /items: List all items.
* GET /item/<item_id>: Retrieve an item by ID.
* POST /item/<item_id>: Create a new item with name and price.
* PUT /item/<item_id>: Update or create an item.
* DELETE /item/<item_id>: Delete an item.

## Setup
1. Build and test the Flask API locally:
```
   bash
   cd app
   docker build -t flask-api .
   docker run -p 5001:5001 flask-api
```
