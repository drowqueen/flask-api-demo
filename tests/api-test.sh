#!/bin/bash

BASE_URL="http://localhost:5001"

request() {
  local method=$1
  local url=$2
  local data=$3

  if [[ -n "$data" ]]; then
    response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "$url")
  else
    response=$(curl -s -w "\n%{http_code}" -X "$method" "$url")
  fi

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')

  echo "$body" | jq

  if [[ "$http_code" =~ ^2 ]]; then
    echo "==> [$method $url] succeeded with HTTP $http_code"
  else
    echo "==> [$method $url] FAILED with HTTP $http_code"
  fi
  echo "--------------------------------------------------"
  sleep 1
}

echo "===== Checking if API is running ====="
request GET "$BASE_URL"

echo "===== Creating item 1 (POST) ====="
request POST "$BASE_URL/item/1" '{"name":"Laptop","price":999.99}'

echo "===== Creating item 2 (POST) ====="
request POST "$BASE_URL/item/2" '{"name":"Phone","price":499.50}'

echo "===== Trying to create item 1 again (should fail) ====="
request POST "$BASE_URL/item/1" '{"name":"Duplicate","price":100.00}'

echo "===== Retrieving item 1 (GET) ====="
request GET "$BASE_URL/item/1"

echo "===== Updating item 2 (PUT) ====="
request PUT "$BASE_URL/item/2" '{"name":"Phone Pro","price":699.00}'

echo "===== Partially updating item 2 (PATCH) ====="
request PATCH "$BASE_URL/item/2" '{"price":749.99}'

echo "===== Listing all items (GET /items) ====="
request GET "$BASE_URL/items"

echo "===== Deleting item 1 (DELETE) ====="
request DELETE "$BASE_URL/item/1"

echo "===== Trying to retrieve deleted item 1 (should 404) ====="
request GET "$BASE_URL/item/1"

echo "===== Final list of items ====="
request GET "$BASE_URL/items"
