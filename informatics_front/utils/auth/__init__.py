import functools

import jwt
from flask import current_app, request, g
from jwt import ExpiredSignatureError
from werkzeug.exceptions import Unauthorized

from informatics_front import RequestUser
from informatics_front.utils.decorators import deprecated


def authenticate():
    g.user = None
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return

    try:
        auth_token = auth_header.split(' ')[1]
    except IndexError:
        raise Unauthorized('Invalid token')

    secret_key = current_app.config.get('SECRET_KEY')
    try:
        user = jwt.decode(auth_token, secret_key, options={'require_exp': True},
                          algorithms=['HS256'])
    except ExpiredSignatureError:
        raise Unauthorized('Token has expired')

    except Exception as e:
        current_app.logger.exception(e)
        raise Unauthorized('Invalid token')

    if 'id' not in user:
        raise Unauthorized('Invalid token')

    g.user = RequestUser(user)


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = getattr(g, 'user', None)
        if user and getattr(user, 'id', False):
            return f(*args, **kwargs)
        raise Unauthorized()
    return decorated_function


@deprecated()
def only_teacher(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
        # user = g.user
        # if not user:
        #     raise Unauthorized('You don\'t have permission '
        #                        'to perform this action')
        # roles = user.get('roles', [])
        # allowed_roles = ('SUPERUSER', 'ADMIN', 'TESTER', 'TEACHER')
        # if set(roles).intersection(set(allowed_roles)):
        #     return f(*args, **kwargs)
        # raise Forbidden('You don\'t have permission to perform this action')
    return decorated_function
