import hashlib

from typing import List

import pytest
from flask import Flask, g
from werkzeug.local import LocalProxy

from informatics_front import User, Problem, CourseModule, CourseModuleInstance, Statement, db
from informatics_front.model import StatementProblem
from informatics_front.model.refresh_tokens import RefreshToken

from informatics_front.utils.auth.make_jwt import generate_refresh_token, generate_jwt_token
from informatics_front.utils.response import jsonify

from informatics_front.view.auth.serializers.auth import UserAuthSerializer

VALID_TIME = 100500
COURSE_VISIBLE = 1


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
def problem(app) -> dict:
    problem = Problem(
        content='foo',
        description='bar',
        memorylimit=100,
        name='baz',
        output_only=True,
        timelimit=3.14,
    )

    db.session.add(problem)
    db.session.commit()

    yield problem

    db.session.delete(problem)
    db.session.commit()


@pytest.yield_fixture
def course_module(app, problem) -> dict:
    statement = Statement(name='foo', summary='bar')
    db.session.add(statement)
    db.session.flush()

    statement_problem = StatementProblem(statement_id=statement.id, problem_id=problem.id, rank=1)
    db.session.add(statement_problem)
    course_module = CourseModule(instance_id=statement.id, module=Statement.MODULE, visible=COURSE_VISIBLE, )
    db.session.add(course_module)
    db.session.commit()

    yield course_module

    db.session.delete(course_module)
    db.session.delete(statement)
    db.session.commit()


@pytest.yield_fixture
def problem(app) -> dict:
    problem = Problem(
        content='foo',
        description='bar',
        memorylimit=100,
        name='baz',
        output_only=True,
        timelimit=3.14,
        hidden=False,
    )

    db.session.add(problem)
    db.session.commit()

    yield problem

    db.session.delete(problem)
    db.session.commit()


@pytest.yield_fixture
def authorized_user(app, user_with_token) -> LocalProxy:
    user_serializer = UserAuthSerializer()
    user_data = user_serializer.dump(user_with_token['user'])

    g.user = user_data.data

    yield g

    del g.user
