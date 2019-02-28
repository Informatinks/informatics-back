import datetime

from sqlalchemy.orm import backref

from informatics_front.model.base import db
from informatics_front.model.user.user import User


class RefreshToken(db.Model):
    __tablename__ = 'refresh_token'
    __table_args__ = (
        db.Index('search_token', 'token'),
        {'schema': 'pynformatics'}
    )

    id = db.Column(db.Integer(), primary_key=True)

    token = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    valid = db.Column(db.Boolean(), default=True, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    user = db.relationship('User', lazy='joined',
                           backref=backref('refresh_tokens', cascade="all, delete-orphan"),
                           single_parent=True)

