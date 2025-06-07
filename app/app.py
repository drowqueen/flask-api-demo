# Import required Flask and Flask-RESTful modules for building the API
from flask import Flask
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

# In-memory dictionary for storing items (Free Tier compatible, no database)
items = {}

# Define request parser for POST and PUT requests with required fields
item_parser = reqparse.RequestParser()
item_parser.add_argument("name", type=str, required=True, help="Name cannot be blank")
item_parser.add_argument("price", type=float, required=True, help="Price cannot be blank")

# Root route for testing API availability
@app.route("/")
def home():
  return jsonify({"message": "API is running"}), 200

# Resource class for individual item endpoints (/item/<id>)
class Item(Resource):
    def get(self, item_id):
        if item_id not in items:
            abort(404, message=f"Item {item_id} not found")
        return items[item_id], 200


    def post(self, item_id):
        if item_id in items:
            abort(400, message=f"Item {item_id} already exists")
        args = item_parser.parse_args()
        items[item_id] = {"name": args["name"], "price": args["price"]}
        return items[item_id], 201


    def put(self, item_id):
        args = item_parser.parse_args()
        items[item_id] = {"name": args["name"], "price": args["price"]}
        return items[item_id], 200


    def delete(self, item_id):
        if item_id not in items:
            abort(404, message=f"Item {item_id} not found")
        del items[item_id]
        return "", 204

# Resource class for listing all items (/items)
class ItemList(Resource):
    def get(self):
        return items, 200

# Register API resources with endpoints
api.add_resource(Item, "/item/<int:item_id>")
api.add_resource(ItemList, "/items")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
