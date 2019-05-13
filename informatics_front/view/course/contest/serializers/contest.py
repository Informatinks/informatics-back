from marshmallow import Schema, fields


class ContestProblemSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    rank = fields.Integer(dump_only=True)


class StatementSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    summary = fields.String(dump_only=True)
    problems = fields.Nested(ContestProblemSchema, many=True)


class ContestSchema(Schema):
    id = fields.Integer(dump_only=True)

    workshop_id = fields.Integer()
    position = fields.Integer()

    time_start = fields.DateTime()
    time_stop = fields.DateTime()
    is_virtual = fields.Boolean()
    virtual_duration = fields.TimeDelta(precision='seconds')
    statement = fields.Nested(StatementSchema)


class ContestConnectionSchema(Schema):
    id = fields.Integer()
    created_at = fields.DateTime()
    contest = fields.Nested(ContestSchema)
