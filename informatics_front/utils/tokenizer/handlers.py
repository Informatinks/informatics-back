from functools import wraps
from typing import Tuple, Callable

from flask import Blueprint, request, g, Flask
from werkzeug.exceptions import Forbidden

from informatics_front.plugins import tokenizer

DEFAULT_ACTION_TTL = 86400  # 1 day


def check_auth(ttl: int):
    """Decorator, which checks signature or provided token request. If token is valid, g is populated
    with decoded payload

    :param ttl: expiration time in seconds which check signature against to
    :return: decorator wrapper
    """

    def wrap(f: Callable) -> Callable:
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            token = request.args.get('token')
            if not token:
                raise Forbidden('No signed token found')
            try:
                g.payload = tokenizer.unpack(token, ttl)
            except Exception as e:
                # catch all exceptions: Signature, Expiration, Bad formatted
                raise Forbidden('Invalid token signature')
            return f(*args, **kwargs)

        return wrapped_f

    return wrap


def run_action(f: Callable, ttl: int = DEFAULT_ACTION_TTL) -> Callable:
    """Handler for using as `view_func` for `blueprint.add_url_rule`

    Request should contain query parameter with signed token.

    :param f: inner function to bind. Can be instance of MethodView or plain function
    :param ttl: expiration time for signature in seconds. If ttl < (current time - token creation time),
           error is raised
    :return: bindable handler function
    """

    @check_auth(ttl)
    @wraps(f)
    def runner():
        return f()

    return runner


def map_action_routes(app: Flask, routes: Tuple = (), url_prefix: str = 'system'):
    """Builds and adds a new blueprint to provided Flask instance.

    :param app: Flask app instance to bind blueprint
    :param routes: routes for blueprint. Inerable, where every element can be assigned
           as (route:str, handler:func, ttl:int)
    :param url_prefix: top level url prefix to prepend blueprint's URL
    :return: None
    """
    blueprint = Blueprint(url_prefix, __name__, url_prefix=f'/{url_prefix}')

    for route, handler, ttl in routes:
        blueprint.add_url_rule(f'/{route}', methods=('GET', 'POST',), view_func=run_action(handler, ttl))

    app.register_blueprint(blueprint)
