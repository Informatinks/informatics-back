import hashlib
from typing import List

import pytest
from flask import Flask

from informatics_front import User, db
from informatics_front.model.refresh_tokens import RefreshToken
from informatics_front.utils.auth.make_jwt import generate_refresh_token, generate_jwt_token


VALID_TIME = 100500


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
def authorized_user(users) -> dict:
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
def token(app: Flask, users: dict):
    user = db.session.query(User).get(users[0]['id'])

    previous_config_data = app.config.get('JWT_TOKEN_EXP')
    app.config['JWT_TOKEN_EXP'] = VALID_TIME

    token = generate_jwt_token(user)
    yield token

    app.config['JWT_TOKEN_EXP'] = previous_config_data


@pytest.yield_fixture
def expired_token(app: Flask, users: dict):
    user = db.session.query(User).get(users[0]['id'])

    previous_config_data = app.config.get('JWT_TOKEN_EXP')
    app.config['JWT_TOKEN_EXP'] = -1

    token = generate_jwt_token(user)
    yield token

    app.config['JWT_TOKEN_EXP'] = previous_config_data