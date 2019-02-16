from marshmallow import fields, Schema

from informatics_front.model import Problem


class ProblemSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    content = fields.String(dump_only=True)
    timelimit = fields.Integer(dump_only=True)
    memorylimit = fields.Integer(dump_only=True)
    description = fields.String(dump_only=True)
    sample_tests_json = fields.Method(serialize='serialize_sample_tests')
    output_only = fields.Boolean(dump_only=True)

    def serialize_sample_tests(self, obj: Problem):
        obj.generateSamplesJson()
        return obj.sample_tests_json
