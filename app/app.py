from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

items = {}

item_parser = reqparse.RequestParser()
item_parser.add_argument("name", type=str, required=True, help="Name cannot be blank")
item_parser.add_argument("price", type=float, required=True, help="Price cannot be blank")

@app.route("/")
def home():
    return {"message": "API is running"}, 200  # Flask auto-jsonifies dicts here

class Item(Resource):
    def get(self, item_id):
        if item_id not in items:
            abort(404, message=f"Item {item_id} not found")
        return items[item_id]  # Return dict

    def post(self, item_id):
        if item_id in items:
            abort(400, message=f"Item {item_id} already exists")
        args = item_parser.parse_args()
        items[item_id] = {"name": args["name"], "price": args["price"]}
        return items[item_id], 201  # Return dict and status

    def put(self, item_id):
        args = item_parser.parse_args()
        items[item_id] = {"name": args["name"], "price": args["price"]}
        return items[item_id]

    def patch(self, item_id):
        if item_id not in items:
            abort(404, message=f"Item {item_id} not found")
        data = request.get_json(force=True)
        if not data:
            abort(400, message="No input data provided")

        item = items[item_id]
        name = data.get("name", item["name"])
        price = data.get("price", item["price"])

        if not isinstance(name, str):
            abort(400, message="Name must be a string")
        if not isinstance(price, (int, float)):
            abort(400, message="Price must be a number")

        items[item_id] = {"name": name, "price": price}
        return items[item_id]

    def delete(self, item_id):
        if item_id not in items:
            abort(404, message=f"Item {item_id} not found")
        del items[item_id]
        return "", 204

class ItemList(Resource):
    def get(self):
        return items  # Return dict of all items

class BulkItemUpload(Resource):
    def post(self):
        data = request.get_json(force=True)

        # ✅ Accept dictionary with "items" key
        if not data or "items" not in data or not isinstance(data["items"], list):
            abort(400, message="Expected JSON with 'items' key containing a list")

        items_list = data["items"]

        created = {}
        errors = {}
        next_id = max(items.keys(), default=0) + 1

        for entry in items_list:
            name = entry.get("name")
            price = entry.get("price")

            if not isinstance(name, str):
                errors[f"invalid_name_{next_id}"] = "Name must be a string"
                continue

            if not isinstance(price, (int, float)):
                errors[f"invalid_price_{next_id}"] = "Price must be a number"
                continue

            items[next_id] = {"name": name, "price": price}
            created[next_id] = items[next_id]
            next_id += 1

        return {
            "created": created,
            "errors": errors
        }, 201

api.add_resource(BulkItemUpload, "/items/bulk")
api.add_resource(Item, "/item/<int:item_id>")
api.add_resource(ItemList, "/items")

def create_app():
    return app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
