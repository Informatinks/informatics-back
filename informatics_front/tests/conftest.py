import pytest
from flask import g

from informatics_front import RequestUser
from informatics_front.utils.auth import authenticate
from informatics_front.app_factory import create_app
from informatics_front.model import db
from informatics_front.model import Role

VALID_TIME = 100500
COURSE_VISIBLE = 1


@pytest.yield_fixture(scope='session')
def app():
    flask_app = create_app(config='informatics_front.config.TestConfig')
    flask_app.before_request_funcs[None].remove(authenticate)

    def fix_current_user():
        g.user = getattr(g, 'user', RequestUser({}))

    flask_app.before_request(fix_current_user)

    with flask_app.app_context():
        # Prevent tests from failing due to existing test database
        # (you might have cancelled previous test suite or something)
        db.drop_all()
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.drop_all()


@pytest.yield_fixture(scope='function')
def local_app():
    flask_app = create_app(config='informatics_front.config.TestConfig')

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


@pytest.yield_fixture(scope='session')
def roles(app):
    short_names = [
        'admin',
        'coursecreator',
        'editingteacher',
        'teacher',
        'student',
        'guest',
        'user',
        'group',
        'ejudge_teacher',
        'editor',
        'testing',
        'source_editor',
        'course_editor',
        'view_courses',
    ]

    roles = [Role(shortname=short_name) for short_name in short_names]
    db.session.add_all(roles)
    db.session.flush()
    roles_ids = {
        name: role.id for name, role in zip(short_names, roles)
    }
    db.session.commit()

    yield roles_ids

    for role in roles:
        db.session.delete(role)

    db.session.commit()
