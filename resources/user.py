from flask.views import MethodView
from flask_smorest import Blueprint, abort 

from schemas import UserSchema
from models import UserModel
from db import db
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from blocklist import BLOCKLIST 

blp = Blueprint("Users", __name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)

    def post(self, user_data):
      if UserModel.query.filter_by(username=user_data["username"]).first():
        abort(409, message="User already exists")

      user = UserModel(
        username = user_data["username"],
        password = sha256.hash(user_data["password"]
      ))

      try:
        db.session.add(user)
        db.session.commit()
      except SQLAlchemyError as e:
        abort(500, message=str(e))

      return user

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
      user = UserModel.query.filter_by(username=user_data["username"]).first()

      if not user:
        abort(401, message="Invalid credentials")

      if not sha256.verify(user_data["password"], user.password):
        abort(401, message="Invalid credentials")

      access_token = create_access_token(identity=user.id, fresh=True)

      return {"access_token": access_token}

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
      user = UserModel.query.get_or_404(user_id)

      return user

    def delete(self, user_id):
      user = UserModel.query.get_or_404(user_id)
      db.session.delete(user)
      db.session.commit()

      return {"message": "User deleted"}, 200
    
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
      jti = get_jwt()["jti"]
      BLOCKLIST.add(jti)
      return {"message": "Successfully logged out"}, 200