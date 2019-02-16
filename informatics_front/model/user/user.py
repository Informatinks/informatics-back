import hashlib

from sqlalchemy.ext.associationproxy import association_proxy

from informatics_front.model.base import db
from informatics_front.model.statement import StatementUser
from informatics_front.utils.auth.make_jwt import generate_jwt_token


class SimpleUser(db.Model):
    RESET_PASSWORD_LENGTH = 20

    __table_args__ = (
        {'schema': 'moodle'}
    )
    __tablename__ = 'mdl_user'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.Unicode(100))
    lastname = db.Column(db.Unicode(100))
    deleted = db.Column('deleted', db.Boolean)
    problems_solved = db.Column(db.Integer)
    password_md5 = db.Column('password', db.Unicode(32))

    statement = db.relationship(
        'Statement',
        secondary=StatementUser.__table__,
        backref='StatementUsers1',
        lazy='dynamic',
    )
    statements = association_proxy('StatementUsers2', 'statement')


class User(SimpleUser):
    __mapper_args__ = {'polymorphic_identity': 'user'}
    username = db.Column(db.Unicode(100))
    email = db.Column(db.Unicode(100))
    city = db.Column(db.Unicode(20))
    school = db.Column(db.Unicode(255))
    problems_week_solved = db.Column(db.Integer)

    roles = db.relationship('Role',
                            secondary='moodle.mdl_role_assignments',
                            lazy='select')

    @property
    def token(self):
        return generate_jwt_token(self)

    @staticmethod
    def check_password(password_md5: str, password: str) -> bool:
        hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
        if password_md5 == hashed_password:
            return True
        return False


class PynformaticsUser(User):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_user_settings'
    __mapper_args__ = {'polymorphic_identity': 'pynformaticsuser'}

    id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_user.id'), primary_key=True)
    main_page_settings = db.Column(db.Text)
