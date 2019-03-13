import pytest

from flask import Flask

from informatics_front.model import User, db
from informatics_front.utils.auth.make_jwt import generate_jwt_token

VALID_TIME = 100500


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
