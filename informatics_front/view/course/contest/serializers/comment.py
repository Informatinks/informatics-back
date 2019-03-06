from marshmallow import Schema, fields

from informatics_front.view.course.contest.serializers.author import CommentAuthorSerializer


class CommentSchema(Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(dump_only=True)
    comment = fields.String(dump_only=True)
    run_id = fields.Integer(dump_only=True, attribute='py_run_id')
    user_id = fields.Integer(dump_only=True)
    author_user = fields.Nested(CommentAuthorSerializer)
