from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm.collections import attribute_mapped_collection

from informatics_front.model.base import db

from informatics_front.utils.json_type import JsonType


class Statement(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_statements'
    __mapper_args__ = {
        'polymorphic_identity': 'statement',
        'concrete': True,
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255))
    summary = db.Column(MEDIUMTEXT)
    numbering = db.Column(db.Integer)
    disable_printing = db.Column('disableprinting', db.Boolean)
    custom_titles = db.Column('customtitles', db.Boolean)
    time_created = db.Column('timecreated', db.Integer)
    time_modified = db.Column('timemodified', db.Integer)
    contest_id = db.Column(db.Integer)
    time_start = db.Column('timestart', db.Integer)
    time_stop = db.Column('timestop', db.Integer)
    olympiad = db.Column(db.Boolean)
    virtual_olympiad = db.Column(db.Boolean)
    virtual_duration = db.Column(db.Integer)
    settings = db.Column(JsonType)

    problems = db.relationship('Problem',
                               secondary='moodle.mdl_statements_problems_correlation')


class StatementProblem(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_statements_problems_correlation'

    id = db.Column(db.Integer, primary_key=True)
    statement_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_statements.id'))
    problem_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_problems.id'))
    rank = db.Column('rank', db.Integer)
    hidden = db.Column('hidden', db.Integer)

    statement = db.relationship('Statement', backref=db.backref('statement_problems'))

    # reference to the "Keyword" object
    problem = db.relationship('Problem', backref=db.backref('StatementProblems'))

    def __init__(self, statement_id, problem_id, rank):
        self.statement_id = statement_id
        self.problem_id = problem_id
        self.rank = rank
        self.hidden = 0
