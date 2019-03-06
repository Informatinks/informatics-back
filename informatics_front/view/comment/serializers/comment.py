from marshmallow import Schema, fields
from informatics_front.view.auth.serializers.auth import UserAuthSerializer


class CommentSchema(Schema):
    id = fields.Integer(dump_only=True)
    comment = fields.String(dump_only=True)
    run_id = fields.Integer(dump_only=True, attribute='py_run_id')
    date = fields.Date(dump_only=True)
    contest_id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    author_user_id = fields.Integer(dump_only=True)
    author_user = fields.Nested(UserAuthSerializer)
    lines = fields.String(dump_only=True)
    is_read = fields.Boolean(dump_only=True)
