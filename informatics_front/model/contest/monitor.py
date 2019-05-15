import enum

from informatics_front.model.base import db
from informatics_front.utils.sqla.types import IntEnum


class WorkshopMonitorType(enum.Enum):
    """
    Тип монитора:
        IOI - по очкам (количество баллов в задаче)
        ACM - по плюсикам (количество решенных задач)
    """
    IOI = 1
    ACM = 2
    LightACM = 3


class WorkshopMonitorUserVisibility(enum.Enum):
    """ Чьи результаты может видеть ученик, свои или общие"""
    FOR_USER_ONLY = 1
    FULL = 2
    DISABLED_FOR_STUDENT = 3


class WorkshopMonitor(db.Model):
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'contest_monitor'

    id = db.Column(db.Integer, primary_key=True)

    workshop_id = db.Column(db.Integer, db.ForeignKey('pynformatics.workshop.id'))
    type = db.Column(
        IntEnum(WorkshopMonitorType),
        default=WorkshopMonitorType.IOI,
        nullable=False
    )

    user_visibility = db.Column(
        IntEnum(WorkshopMonitorUserVisibility),
        default=WorkshopMonitorUserVisibility.FULL,
        nullable=False
    )

    with_penalty_time = db.Column(db.Boolean, default=False)
    freeze_time = db.Column(db.DateTime)

    workshop = db.relationship(
        'WorkShop',
        backref=db.backref('monitors', cascade='all, delete-orphan')
    )

    def is_for_user_only(self):
        return self.type == WorkshopMonitorUserVisibility.FOR_USER_ONLY

    def is_disabled_for_students(self):
        return self.type == WorkshopMonitorUserVisibility.DISABLED_FOR_STUDENT
