from marshmallow import Schema, fields

from informatics_front.view.course.contest.serializers.contest import ContestSchema


class WorkshopSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    is_visible = fields.Bool(dump_only=True, attribute='visibility')
    contests = fields.Nested(ContestSchema, many=True)
