import logging
from sqlalchemy.ext.declarative import declared_attr

from informatics_front.model.base import db
from informatics_front.utils.functions import (
    attrs_to_dict, 
)
from informatics_front.utils.json_type import (
    JsonType,
    MutableDict,
)


log = logging.getLogger(__name__)


class StandingsMixin:
    __table_args__ = {'schema': 'pynformatics'}

    @declared_attr
    def json(cls):
        return db.Column('json', MutableDict.as_mutable(JsonType))

    def update(self, user):
        if not self.json:
            self.json = {}

        if str(user.id) not in self.json:
            self.json[str(user.id)] = {
                **attrs_to_dict(user, 'firstname', 'lastname'),
            }


class ProblemStandings(StandingsMixin, db.Model):
    __tablename__ = 'problem_standings'
    __table_args__ = {'schema': 'pynformatics'}

    problem_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_problems.id'), primary_key=True)
    problem = db.relationship('EjudgeProblem', backref=db.backref('standings', uselist=False, lazy='joined'))


class StatementStandings(StandingsMixin, db.Model):
    __tablename__ = 'statement_standings'

    statement_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_statements.id'), primary_key=True)
    statement = db.relationship('Statement', backref=db.backref('standings', uselist=False, lazy='joined'))
