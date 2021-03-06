import datetime

from informatics_front.model.base import db


class ContestConnection(db.Model):
    __table_args__ = (
        db.UniqueConstraint('user_id', 'contest_id', name='_contest_user_uc'),
        {'schema': 'pynformatics'},
    )
    __tablename__ = 'contest_connection'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    contest_id = db.Column(
        db.Integer,
        db.ForeignKey('pynformatics.contest.id', ondelete='CASCADE'),
    )

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    contest = db.relationship(
        'Contest',
        backref=db.backref('connections', cascade='all, delete-orphan')
    )
