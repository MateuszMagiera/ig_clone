from models import PostModel, UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from schemas import PostSchema
from db import db
from flask import jsonify,render_template,request,session,send_from_directory
import os
import imghdr
import uuid
from werkzeug.utils import secure_filename
from helpers.helpers import validate_iamge

blp = Blueprint('Posts', __name__,description="Operations on posts")



@blp.route("/posts")
class PostsList(MethodView):
    def get(self):
        posts = PostModel.query.all()
        post_schema = PostSchema(many=True)
        serialized_posts = post_schema.dump(posts)
        if "text/html" in request.headers.get('Accept', ''):
            return render_template("posts.html", posts=serialized_posts)
        else:
            return serialized_posts

    @jwt_required()
    @blp.arguments(PostSchema)
    @blp.response(201, PostSchema)
    def post(self, post_data):
        user_id = get_jwt_identity()
        post = PostModel(user_id=user_id, **post_data)

        try:
            db.session.add(post)
            db.session.commit()
        except SQLAlchemyError as err:
            abort(500, message=f'An error occurred when creating the post: {err}')

        return post


@blp.route("/posts/<string:post_id>")
class Post(MethodView):
    @blp.response(200, PostSchema)
    def get(self,post_id):
        post = PostModel.query.get_or_404(post_id)
        return post

    @jwt_required()
    @blp.response(200, PostSchema)
    def delete(self,post_id):
        post = PostModel.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return {"message": f"Post with id {post_id} deleted successfully"}
