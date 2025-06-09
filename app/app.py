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

api.add_resource(Item, "/item/<int:item_id>")
api.add_resource(ItemList, "/items")

def create_app():
    return app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
