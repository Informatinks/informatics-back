from informatics_front.model.base import db


class LanguageContest(db.Model):
    __table_args__ = (
        db.UniqueConstraint('language_id', 'contest_id', name='_language_contest_uc'),
        {'schema': 'pynformatics'},
    )
    __tablename__ = 'language_contest'

    id = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(
        db.Integer,
        db.ForeignKey('pynformatics.languages.id', ondelete='CASCADE'))
    contest_id = db.Column(
        db.Integer,
        db.ForeignKey('pynformatics.contest.id', ondelete='CASCADE'))


class Language(db.Model):
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'languages'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer(), nullable=False)
    title = db.Column(db.String(32), nullable=False)
    mode = db.Column(db.String(32), nullable=True)
