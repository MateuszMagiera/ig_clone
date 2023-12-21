from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=False)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserUpdateSchema(Schema):
    username = fields.Str()


class PostSchema(Schema):
    id = fields.Int(dump_only=True,load_only=True)
    title = fields.Str(required=True, default="Default Title")
    content = fields.Str(required=True)
    created_at = fields.Date(dump_only=True)
    user_id = fields.Int(load_only=True, required=False, dump_only=True)
