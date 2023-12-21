import uuid
from flask import request, render_template, redirect, flash, url_for
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import ValidationError
from blocklist import BLOCKLIST
from schemas import UserSchema, UserUpdateSchema
from models import UserModel, PostModel
from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

blp = Blueprint("Users", __name__, description="Operation on users")


@blp.route("/")
class Home(MethodView):
    def get(self):
        return render_template('home.html')


@blp.route("/users")
class UserList(MethodView):
    @blp.response(200, UserSchema(many=True))
    def get(self):
        return UserModel.query.all()

    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self,user_data):
        user = UserModel(**user_data)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(400, message="This user already exists")
        except SQLAlchemyError as e:
            print(f"SQLAlchemy error: {e}")
            abort(500, message="An error occurred when creating an user")
        return user


@blp.route("/users/<string:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self,user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self,user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}, 200


@blp.route("/register")
class UserRegister(MethodView):
    def get(self):
        return render_template('register.html')

    def post(self):
        if request.content_type == "application/x-www-form-urlencoded":
            user_schema = UserSchema()
            try:
                # Validate form data against UserSchema
                user_data = user_schema.load(request.form)
            except ValidationError as err:
                # Handle validation errors
                for message in err.messages.values():
                    flash(' '.join(message), 'error')
                return redirect(url_for('Users.UserRegister'))
        else:
            # Handle JSON data
            user_schema = UserSchema()
            try:
                user_data = user_schema.load(request.get_json())
            except ValidationError as err:
                return {"message": "Invalid data format", "errors": err.messages}, 400

        # Check if user already exists
        if UserModel.query.filter_by(username=user_data["username"]).first():
            message = 'A user with that username already exists'
            flash(message, 'error')
            return redirect(url_for('Users.UserRegister'))

        # Create new user
        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()

        flash('User created successfully', 'success')
        return redirect(url_for('Users.UserLogin'))


@blp.route("/login")
class UserLogin(MethodView):
    def get(self):
        # Render the login form for frontend
        return render_template("login.html")

    def post(self):
        # Check if the request is from the frontend form
        if request.content_type == 'application/x-www-form-urlencoded':
            username = request.form.get('username')
            password = request.form.get('password')
        else:
            # Process JSON data for API requests
            user_data = request.get_json()
            if not user_data:
                abort(400, message="Invalid request format")
            username = user_data.get('username')
            password = user_data.get('password')

        # Validate credentials
        user = UserModel.query.filter(UserModel.username == username).first()
        if user and pbkdf2_sha256.verify(password, user.password):
            access_token = create_access_token(identity=user.id)

            if request.content_type == 'application/x-www-form-urlencoded':
                return redirect(url_for('Posts.PostsList'))  # Redirect to /posts page for frontend
            else:
                return {"access_token": access_token}, 200  # Return JSON for API requests

        if request.content_type == 'application/x-www-form-urlencoded':
            flash('Invalid credentials.')  # Flash message for frontend
            return redirect(url_for('Users.UserLogin'))  # Redirect back to login
        else:
            abort(401, message='Invalid credentials.')  # JSON error for API


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        if request.content_type == 'application/x-www-form-urlencoded':
            return redirect(url_for('Home'))
        else:
            return {"message": "Successfully logged out"}, 200



