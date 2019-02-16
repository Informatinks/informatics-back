from marshmallow import fields, Schema


class ProblemSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    content = fields.String(dump_only=True)
    timelimit = fields.Integer(dump_only=True)
    memorylimit = fields.Integer(dump_only=True)
    description = fields.String(dump_only=True)
    sample_tests_json = fields.String(dump_only=True)
    output_only = fields.Boolean(dump_only=True)
