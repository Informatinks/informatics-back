import datetime
from enum import Enum

from informatics_front.model.base import db
from informatics_front.model.workshop.contest_connection import ContestConnection
from informatics_front.utils.sqla.types import IntEnum


class ContestProtocolVisibility(Enum):
    FULL = 1
    FIRST_BAD_TEST = 2
    INVISIBLE = 3


class Contest(db.Model):
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'contest'

    id = db.Column(db.Integer, primary_key=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey('pynformatics.workshop.id'))
    statement_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_statements.id'))
    author_id = db.Column(db.Integer)
    position = db.Column(db.Integer, default=1)

    protocol_visibility = db.Column(IntEnum(ContestProtocolVisibility),
                                    default=ContestProtocolVisibility.FULL,
                                    nullable=False)

    is_virtual = db.Column(db.Boolean, default=False)
    time_start = db.Column(db.DateTime)
    time_stop = db.Column(db.DateTime)
    virtual_duration = db.Column(db.Interval, default=datetime.timedelta(seconds=0))

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    statement = db.relationship('Statement')
    workshop = db.relationship('WorkShop', back_populates='contests')

    def _is_available_by_duration(self) -> bool:
        """ Checks date time restrictions """
        current_time = datetime.datetime.utcnow()
        if self.time_start is not None and self.time_start > current_time:
            return False
        if self.time_stop is not None and self.time_stop < current_time:
            return False
        return True

    def _is_available_for_connection(self, cc: ContestConnection) -> bool:
        """ Checks if virtual contest is not expired for ContestConnection """
        if not self.is_virtual:
            return True

        current_time = datetime.datetime.utcnow()
        if cc.created_at + self.virtual_duration < current_time:
            return False

        return True

    def is_available(self, cc):
        return self._is_available_by_duration() and \
               self._is_available_for_connection(cc)
