from models import PostModel, UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.post import PhotoModel
from schemas import PostSchema
from db import db
from flask import jsonify, render_template, request, session, send_from_directory, current_app, session, url_for
import os
import imghdr
import uuid
from werkzeug.utils import secure_filename
from helpers.helpers import validate_image

blp = Blueprint('Posts', __name__,description="Operations on posts")


@blp.route("/posts")
class PostsList(MethodView):
    def get(self):
        posts = PostModel.query.all()
        post_schema = PostSchema(many=True)
        serialized_posts = post_schema.dump(posts)

        for post in serialized_posts:
            image_filename = post.get('image_filename')
            if post['image_filename']:
                post['image_url'] = url_for('static',filename=f'image_uploads/{post["image_filename"]}')
        if "text/html" in request.headers.get('Accept', ''):
            return render_template("posts.html", posts=serialized_posts)
        else:
            return serialized_posts

    @blp.route("/posts")
    class PostsList(MethodView):
        def get(self):
            posts = PostModel.query.all()
            post_schema = PostSchema(many=True)
            serialized_posts = post_schema.dump(posts)

            for post in serialized_posts:
                image_filename = post.get('image_filename')  # Use .get() to safely retrieve the value
                if image_filename:  # Check if image_filename is not None or empty
                    post['image_url'] = url_for('static', filename=f'image_uploads/{image_filename}')
            if "text/html" in request.headers.get('Accept', ''):
                return render_template("posts.html", posts=serialized_posts)
            else:
                return serialized_posts

        @jwt_required()
        @blp.arguments(PostSchema)
        @blp.response(201, PostSchema)
        def post(self, post_data):
            user_id = get_jwt_identity()

            # Deserialize the request data
            post_schema = PostSchema()
            post_data = post_schema.load(request.json)

            # Extract title and content from the deserialized data
            title = post_data['title']
            content = post_data['content']

            # Create the post object
            new_post = PostModel(title=title, content=content, user_id=user_id)

            try:
                # Add the post to db
                db.session.add(new_post)
                db.session.commit()

                # Process photos
                photos_data = post_data.get('photos', [])
                for photo_data in photos_data:
                    filename = photo_data.get('filename')
                    description = photo_data.get('description')

                    # Create and add photo to the post
                    new_photo = PhotoModel(filename=filename, description=description, post=new_post)
                    db.session.add(new_photo)
                    db.session.commit()

                    # Serialize the response
                    response_data = post_schema.dump(new_post)

                    return jsonify(response_data), 201
            except Exception as e:
                # Rollback changes if an error occurs
                db.session.rollback()
                return jsonify({"message": "An error occurred while creating the post.", "error": str(e)}), 500

        def delete(self):
            db.session.query(PostModel).delete()
            db.session.commit()
            return jsonify({"message": "All posts deleted successfully."}), 200


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

