## Simple Flask API Demo With Nginx Reverse Proxy 

### Prerequisites 
* AWS Credentials: Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in GitHub Secrets.
* ssh key for the instances from aws 
* Terraform: Version 1.8.0 or higher
* Terragrunt: Version 0.55.1 or higher
* awscli version 2
* Docker, python3

### Features
* In-Memory Storage: Uses a dictionary for simplicity (AWS Free Tier compatible, no database needed).
* Request Validation: Uses reqparse to enforce required fields (name, price).
* Error Handling: Returns appropriate HTTP status codes (e.g., 404 for not found, 400 for bad requests).
* Nginx Integration: The API listens on port 5001.

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

curl  http://127.0.0.1:5001
curl -X POST -H "Content-Type: application/json" -d '{"name":"Laptop","price":999.99}' http://localhost:5001/item/1
curl http://localhost:5001/item/1
```
