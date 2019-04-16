import datetime

from informatics_front.model.base import db


class ContestConnection(db.Model):
    __table_args__ = (
        db.UniqueConstraint('user_id', 'contest_instance_id', name='_contest_user_uc'),
        {'schema': 'pynformatics'},
    )
    __tablename__ = 'contest_connection'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    contest_instance_id = db.Column(
        db.Integer,
        db.ForeignKey('pynformatics.contest_instance.id', ondelete='CASCADE'),
    )

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    contest_instance = db.relationship(
        'ContestInstance',
        backref=db.backref('connections', cascade='all, delete-orphan')
    )
