from informatics_front.model.base import db


class Language(db.Model):
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'languages'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)

    # contests = db.relationship('Contest', secondary='LanguageContest')


class LanguageContest(db.Model):
    __table_args__ = (
        db.UniqueConstraint('language_id', 'contest_id', name='_language_contest_uc'),
        db.Index('contest_id'),
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
