import datetime

from sqlalchemy.schema import ForeignKeyConstraint

from informatics_front.model.base import db


class Comment(db.Model):
    __tablename__ = "mdl_run_comments"
    __table_args__ = {'schema': 'ejudge'}

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    contest_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, nullable=False)
    author_user_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_user.id'), nullable=False)
    author_user = db.relation("User", uselist=False, lazy='select')
    run_id = db.Column(db.Integer)  # deprecated
    lines = db.Column(db.Text)
    comment = db.Column(db.Text)
    is_read = db.Column(db.Boolean)
    py_run_id = db.Column(db.Integer)

    def get_by(run_id, contest_id):
        try:
            return db.session.query(Comment).filter(Comment.run.run_id == int(run_id)).filter(
                Comment.contest_id == int(contest_id)).first()
        except:
            return None

    get_by = staticmethod(get_by)
