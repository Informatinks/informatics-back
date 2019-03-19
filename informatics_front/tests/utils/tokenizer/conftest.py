import pytest

from informatics_front import create_app, authenticate

SERVER_NAME = 'TEST_APP'
ACTION_SECRET_KEY = 'ACTION_SECRET_KEY'


@pytest.yield_fixture(scope='function')
def local_app():
    flask_app = create_app()
    flask_app.config['SERVER_NAME'] = SERVER_NAME
    flask_app.config['ACTION_SECRET_KEY'] = ACTION_SECRET_KEY

    flask_app.before_request_funcs[None].remove(authenticate)

    yield flask_app


@pytest.yield_fixture(scope='function')
def local_client(local_app):
    """A Flask test client. An instance of :class:`flask.testing.TestClient`
    by default.
    """
    with local_app.app_context():
        with local_app.test_client() as test_client:
            yield test_client
