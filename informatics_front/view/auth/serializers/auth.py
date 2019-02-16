from marshmallow import Schema, fields


class RoleAuthSerializer(Schema):
    shortname = fields.String(dump_only=True)


class UserAuthSerializer(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(dump_only=True)
    firstname = fields.String(dump_only=True)
    lastname = fields.String(dump_only=True)
    email = fields.String(dump_only=True)
    token = fields.String(dump_only=True)
    refresh_token = fields.String(dump_only=True)
