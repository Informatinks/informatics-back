from informatics_front.model import db


class Group(db.Model):
    __table_args__ = (
        {'schema': 'moodle'}
    )
    __tablename__ = 'mdl_ejudge_group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(100))
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer)
    visible = db.Column(db.Integer)

    users = db.relationship('User', secondary='moodle.mdl_ejudge_group_users')

    # owner = db.relationship('SimpleUser', backref=db.backref('groups', lazy='select'), lazy='joined')


class UserGroup(db.Model):
    __table_args__ = (
        db.UniqueConstraint('user_id', 'group_id', name='group_id'),
        {'schema': 'moodle'},
    )
    __tablename__ = 'mdl_ejudge_group_users'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_ejudge_group.id'))

    user = db.relationship('SimpleUser',
                           backref=db.backref('user_groups', cascade="all, delete-orphan"),
                           single_parent=True
                           )
    group = db.relationship('Group', backref=db.backref('user_groups', lazy='select'))
