from marshmallow import Schema, fields

from informatics_front.utils.enums import WorkshopConnectionStatus
from informatics_front.utils.marshmallow import ValueEnum


class WorkshopConnectionSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    workshop_id = fields.Integer(dump_only=True)
    status = ValueEnum(enum=WorkshopConnectionStatus, dump_only=True)
