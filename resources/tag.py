import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort 
from schemas import TagSchema, TagAndItemSchema
from models import TagModel, StoreModel, ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("tag", __name__, description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all()
    
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data, store_id=store_id)  

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag
    
@blp.route("/item/<int:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagAndItemSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)
        
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:    
            abort(500, message=str(e))

        return tag
    
    @blp.response(201, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)
        
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:    
            abort(500, message=str(e))

        return {"message": "Item removed form tag", "item": item,  "tag": tag}  
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(
            202, 
            description="Tag deleted",
            example={"message": "Tag deleted"}
          )
    @blp.alt_response(400, description="Returned if the tag is assigned to one or more items")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted"}
        abort(400, message="Could not delete, tag is assigned to one or more items")
          