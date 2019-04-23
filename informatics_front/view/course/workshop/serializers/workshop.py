from marshmallow import Schema, fields

from informatics_front.view.course.contest.serializers.contest import ContestSchema


class WorkshopSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    visibility = fields.Bool(dump_only=True)
    contests = fields.Nested(ContestSchema, many=True)
