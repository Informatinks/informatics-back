import datetime
from typing import Optional

import jwt
from flask import current_app

from informatics_front.view.auth.serializers.auth import RoleAuthSerializer


def generate_auth_token(user: 'User') -> str:
    roles_serializer = RoleAuthSerializer(many=True)
    roles = roles_serializer.dumps(user.roles)

    expiration = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=current_app.config.get('JWT_TOKEN_EXP'))

    d = {
        'id': user.id,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'roles': roles.data,
        'exp': expiration,
    }
    token: bytes = jwt.encode(d, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token.decode('utf-8')


def generate_refresh_token(user: 'User') -> str:
    expiration = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=current_app.config.get('JWT_REFRESH_TOKEN_EXP', ))
    d = {
        'user_id': user.id,
        'exp': expiration,
    }
    token = jwt.encode(d, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token.decode('utf-8')


def decode_jwt_token(token: str) -> Optional[dict]:
    token_options = {'require_exp': True}
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'],
                          options=token_options)
    except jwt.PyJWTError:
        return None
