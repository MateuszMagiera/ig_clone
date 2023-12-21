from flask import Flask, jsonify
from flask_smorest import Api
from resources.user import blp as UserBlueprint
from resources.post import blp as PostBlueprint
from db import db
from flask_jwt_extended import JWTManager
from blocklist import BLOCKLIST
from flask_migrate import Migrate


def create_app(db_url=None):
    app = Flask(__name__)
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png"]
    app.config["UPLOAD_PATH"] = "image_uploads"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app)
    migrate = Migrate(app,db)
    api = Api(app)

    app.config["SECRET_KEY"] = "test"
    app.config["JWT_SECRET_KEY"] = "test"
    jwt=JWTManager(app)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ), 401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ), 401
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(error):
        return (
            jsonify(
                {
                    "description": "The token has been revoked.", "error": "token_revoked"
                }
            ), 401
        )

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header,jwt_payload):
        return jwt_payload['jti'] in BLOCKLIST

    @app.before_request
    def create_tables():
        db.create_all()

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(PostBlueprint)

    return app





