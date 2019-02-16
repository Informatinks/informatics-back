import pytest

from informatics_front import create_app, authenticate, db
from informatics_front.model import Role


@pytest.yield_fixture(scope='session')
def app():
    flask_app = create_app()
    flask_app.before_request_funcs[None].remove(authenticate)

    with flask_app.app_context():
        # Prevent tests from failing due to existing test database
        # (you might have cancelled previous test suite or something)
        db.drop_all()
        db.create_all()

    yield flask_app


@pytest.fixture(scope='session')
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

    return roles_ids
