import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort 
from schemas import ItemSchema, ItemSchemaUodate
from models import ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("items", __name__, description="Operations on items")

@blp.route("/item/<string:item_id>")
class Item(MethodView):
    
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        try:
            return items[item_id]
        except KeyError:
            abort(404, message=f"Item {item_id} not found") 

    def delete(self, item_id):
        try:
            del items[item_id]
            return {"message": f'items[item_id] deleted'}
        except KeyError:
            abort(404, message=f"Item {item_id} not found")

    @blp.arguments(ItemSchemaUodate)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item_data = request.get_json()
            
        try:
          item = items[item_id]
          item |= item_data

          return item
        except KeyError:
            abort(404, message=f"Item {item_id} not found")

@blp.route("/item")
class ItemList(MethodView):
    
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return items.values()
    
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item")

        return item, 201
    