import hashlib

from sqlalchemy.ext.associationproxy import association_proxy

from informatics_front.model.base import db
from informatics_front.model.statement import StatementUser
from informatics_front.utils.auth.make_jwt import generate_auth_token


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
        return generate_auth_token(self)

    @classmethod
    def check_password(cls, password_md5: str, password: str) -> bool:
        return password_md5 == cls.hash_password(password)

    @staticmethod
    def hash_password(plan_password: str) -> str:
        """Returns MD5 hash for plan password string.
        Raises ValueError if password string is invalid.

        :param plan_password: password string to hash
        :return: hashed password
        """
        return hashlib.md5(plan_password.encode('utf-8')).hexdigest()


class PynformaticsUser(User):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_user_settings'
    __mapper_args__ = {'polymorphic_identity': 'pynformaticsuser'}

    id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_user.id'), primary_key=True)
    main_page_settings = db.Column(db.Text)
