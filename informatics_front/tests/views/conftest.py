import hashlib
import pytest
from flask import g
from typing import List
from werkzeug.local import LocalProxy

from informatics_front import User, db
from informatics_front.model.refresh_tokens import RefreshToken
from informatics_front.utils.auth.make_jwt import generate_refresh_token
from informatics_front.view.auth.serializers.auth import UserAuthSerializer, RoleAuthSerializer


@pytest.yield_fixture
def users(app) -> List[dict]:
    password = 'simple_pass'
    password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    users = [
        User(username=f'user{i}', password_md5=password_hash) for i in range(1, 3)
    ]
    db.session.add_all(users)
    db.session.flush()

    users_json = [
        {'user_name': user.username,
         'id': user.id,
         'password': password} for user in users
    ]

    db.session.commit()

    yield users_json

    for u in users:
        db.session.delete(u)

    db.session.commit()


@pytest.yield_fixture
def user_with_token(users) -> dict:
    user_id = users[0]['id']
    user = db.session.query(User).get(user_id)
    token = generate_refresh_token(user)

    rt = RefreshToken(token=token, user_id=user_id)

    db.session.add(rt)
    db.session.commit()

    yield {'user': user, 'token': token}

    db.session.delete(rt)
    db.session.commit()


@pytest.yield_fixture
def authorized_user(app, user_with_token) -> LocalProxy:
    roles_serializer = RoleAuthSerializer(many=True)
    roles = roles_serializer.dumps(user_with_token['user'].roles)
    user_data = {
        'id': user_with_token['user'].id,
        'roles': roles.data,
    }

    g.user = user_data

    yield g

    del g.user
