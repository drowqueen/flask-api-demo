from flask import Flask
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

items = {}

item_parser = reqparse.RequestParser()
item_parser.add_argument("name", type=str, required=True, help="Name cannot be blank")
item_parser.add_argument("price", type=float, required=True, help="Price cannot be blank")

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


class ItemList(Resource):
    def get(self):
        return items, 200


api.add_resource(Item, "/item/<int:item_id>")
api.add_resource(ItemList, "/items")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
