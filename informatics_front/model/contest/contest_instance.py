from informatics_front.model.base import db


class ContestInstance(db.Model):
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'contest_instance'

    id = db.Column(db.Integer, primary_key=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey('pynformatics.workshop.id'))
    contest_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_statements.id'))
    author_id = db.Column(db.Integer)
    position = db.Column(db.Integer, default=1)

    is_virtual = db.Column(db.Boolean, default=False)
    time_start = db.Column(db.DateTime)
    time_stop = db.Column(db.DateTime)
    virtual_duration = db.Column(db.Integer)

    contest = db.relationship('Statement')
    workshop = db.relationship('WorkShop')
