from marshmallow import Schema, fields

from informatics_front.view.course.contest.serializers.contest import ContestSchema


class UserSchema(Schema):
    id = fields.Integer()
    firstname = fields.String()
    lastname = fields.String()


class MonitorSchema(Schema):
    contests = fields.Nested(ContestSchema, many=True)
    users = fields.Nested(UserSchema, many=True)
    results = fields.Raw()
    type = fields.String()


monitor_schema = MonitorSchema()
