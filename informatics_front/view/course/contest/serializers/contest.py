from marshmallow import Schema, fields


class ContestProblemSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    rank = fields.Integer(dump_only=True)


class ContestSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    summary = fields.String(dump_only=True)
    problems = fields.Nested(ContestProblemSchema, many=True)

