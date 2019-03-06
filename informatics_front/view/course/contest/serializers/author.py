from marshmallow import Schema, fields


class CommentAuthorSerializer(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(dump_only=True)
    firstname = fields.String(dump_only=True)
    lastname = fields.String(dump_only=True)
