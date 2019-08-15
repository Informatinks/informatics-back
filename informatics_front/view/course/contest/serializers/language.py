from marshmallow import fields, Schema


class LanguageSchema(Schema):
    id = fields.Integer(dump_only=True)
    code = fields.Integer(dump_only=True)
    title = fields.String(dump_only=True)
    mode = fields.String(dump_only=True)
