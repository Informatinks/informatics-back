import enum

from informatics_front.model.base import db
from informatics_front.utils.sqla.types import IntEnum


class WorkshopConnectionStatus(enum.Enum):
    APPLIED = 1  # подана заявка, еще не одобрена
    ACCEPTED = 2  # принят на курс
    DISQUALIFIED = 3  # отчислен с курса (после ACCEPTED)
    REJECTED = 4  # заявка не одобрена (после APPLIED)


class WorkshopConnection(db.Model):
    __table_args__ = (
        db.UniqueConstraint('user_id', 'workshop_id', name='_workshop_user_uc'),
        {'schema': 'pynformatics'},
    )
    __tablename__ = 'workshop_connection'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('moodle.mdl_user.id'), index=True)
    workshop_id = db.Column(
        db.Integer,
        db.ForeignKey('pynformatics.workshop.id', ondelete='CASCADE', name='fk_course_id'),
        nullable=False
    )

    status = db.Column(
        IntEnum(WorkshopConnectionStatus),
        default=WorkshopConnectionStatus.ACCEPTED,  # TODO: возможно, поменять на APPLIED
        nullable=False
    )

    user = db.relationship('User')

    workshop = db.relationship(
        'WorkShop',
        backref=db.backref('connections', cascade='all, delete-orphan')
    )

    def is_accepted(self):
        return self.status == WorkshopConnectionStatus.ACCEPTED

    def __repr__(self):
        return (
            f'<WorkshopConnection '
            f'id="{self.id}" '
            f'workshop_id="{self.workshop_id}" '
            f'user_id="{self.user_id}">'
        )
