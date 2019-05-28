from informatics_front.model.base import db
from informatics_front.utils.enums import WorkshopStatus, WorkshopVisibility
from informatics_front.utils.sqla.types import IntEnum


class WorkShop(db.Model):
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'workshop'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, default='Время Сборов.')
    status = db.Column(IntEnum(WorkshopStatus), nullable=False,
                       default=WorkshopStatus.DRAFT)
    visibility = db.Column(IntEnum(WorkshopVisibility), nullable=False,
                           default=WorkshopVisibility.PRIVATE)

    access_token = db.Column(db.String(32), nullable=False)
    contests = db.relationship('Contest', back_populates='workshop')
