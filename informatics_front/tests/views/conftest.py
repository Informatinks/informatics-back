import hashlib
from contextlib import contextmanager
from typing import List

import pytest
from flask import g
from werkzeug.local import LocalProxy

from informatics_front import RequestUser
from informatics_front.model import StatementProblem, Problem, Statement, Comment, db, Group, UserGroup
from informatics_front.model import User
from informatics_front.model.contest.contest import Contest
from informatics_front.model.problem import EjudgeProblem
from informatics_front.model.refresh_tokens import RefreshToken
from informatics_front.model.workshop.contest_connection import ContestConnection
from informatics_front.model.workshop.workshop import WorkShop, WorkshopStatus
from informatics_front.model.workshop.workshop_connection import WorkshopConnection, WorkshopConnectionStatus
from informatics_front.utils.auth.make_jwt import generate_refresh_token
from informatics_front.view.auth.serializers.auth import RoleAuthSerializer

VALID_TIME = 100500
COURSE_VISIBLE = 1

NESTED_EJUDGE_PROBLEM_SEQ = 1


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

    g.user = RequestUser(id=user_with_token['user'].id, roles=roles.data)

    yield g

    del g.user


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


@contextmanager
def create_workshop(statement, status: WorkshopStatus):
    w = WorkShop(status=status)
    db.session.add(w)
    db.session.flush()

    ci = Contest(workshop_id=w.id, statement_id=statement.id)
    db.session.add(ci)
    db.session.flush()

    db.session.commit()

    yield {'workshop': w, 'contest': ci}

    db.session.delete(ci)
    db.session.delete(w)
    db.session.commit()


@pytest.yield_fixture
def ongoing_workshop(app, statement):
    with create_workshop(statement, WorkshopStatus.ONGOING) as ret:
        yield ret


@pytest.yield_fixture
def draft_workshop(app, statement):
    with create_workshop(statement, WorkshopStatus.DRAFT) as ret:
        yield ret


@contextmanager
def create_workshop_connection(workshop, user_id, status: WorkshopConnectionStatus):
    wc = WorkshopConnection(workshop_id=workshop.id, user_id=user_id, status=status)
    db.session.add(wc)
    db.session.commit()

    yield wc

    db.session.delete(wc)


@pytest.yield_fixture
def applied_workshop_connection(authorized_user, ongoing_workshop):
    user_id = g.user['id']
    w = ongoing_workshop['workshop']
    with create_workshop_connection(w, user_id, WorkshopConnectionStatus.APPLIED) as ret:
        yield ret


@pytest.yield_fixture
def accepted_workshop_connection(authorized_user, ongoing_workshop):
    user_id = g.user['id']
    w = ongoing_workshop['workshop']
    with create_workshop_connection(w, user_id, WorkshopConnectionStatus.ACCEPTED) as ret:
        yield ret


@pytest.yield_fixture
def disqualified_workshop_connection(authorized_user, ongoing_workshop):
    user_id = g.user['id']
    w = ongoing_workshop['workshop']
    with create_workshop_connection(w, user_id, WorkshopConnectionStatus.DISQUALIFIED) as ret:
        yield ret


@pytest.yield_fixture
def rejected_workshop_connection(authorized_user, ongoing_workshop):
    user_id = g.user['id']
    w = ongoing_workshop['workshop']
    with create_workshop_connection(w, user_id, WorkshopConnectionStatus.REJECTED) as ret:
        yield ret


@pytest.yield_fixture
def draft_workshop_connection(authorized_user, draft_workshop):
    user_id = g.user['id']
    w = draft_workshop['workshop']
    with create_workshop_connection(w, user_id, WorkshopConnectionStatus.APPLIED) as ret:
        yield ret


@pytest.yield_fixture
def contest_connection(authorized_user, ongoing_workshop):
    user_id = g.user['id']
    contest = ongoing_workshop['contest']

    cc = ContestConnection(user_id=user_id, contest_id=contest.id)
    db.session.add(cc)
    db.session.commit()

    yield cc

    db.session.delete(cc)
    db.session.commit()


@pytest.yield_fixture
def statement(app) -> dict:
    # We have to use nested indexes because default seq with primary keys
    # is not working correctly with association_proxy (???)
    # also we can't even remove it because
    # it is circular dependency for SQLAlchemy
    global NESTED_EJUDGE_PROBLEM_SEQ
    ejudge_problems = [
        EjudgeProblem.create(
            ejudge_prid=NESTED_EJUDGE_PROBLEM_SEQ,
            contest_id=1,
            ejudge_contest_id=1,
            problem_id=1,
        ),
        EjudgeProblem.create(
            ejudge_prid=NESTED_EJUDGE_PROBLEM_SEQ + 1,
            contest_id=2,
            ejudge_contest_id=1,
            problem_id=2,
        ),
        EjudgeProblem.create(
            ejudge_prid=NESTED_EJUDGE_PROBLEM_SEQ + 2,
            contest_id=3,
            ejudge_contest_id=2,
            problem_id=1,
        )
    ]
    NESTED_EJUDGE_PROBLEM_SEQ += 3

    db.session.add_all(ejudge_problems)
    db.session.flush(ejudge_problems)
    problems = [
        Problem(name='Problem1', pr_id=ejudge_problems[0].ejudge_prid),
        Problem(name='Problem2', pr_id=ejudge_problems[1].ejudge_prid),
        Problem(name='Problem3', pr_id=ejudge_problems[2].ejudge_prid),
    ]
    db.session.add_all(problems)
    db.session.flush(problems)
    statement = Statement(name='foo', summary='bar')
    db.session.add(statement)
    db.session.flush()

    statement_problems = [
        StatementProblem(problem_id=problems[0].id,
                         statement_id=statement.id,
                         rank=1),
        StatementProblem(problem_id=problems[1].id,
                         statement_id=statement.id,
                         rank=2),
        StatementProblem(problem_id=problems[2].id,
                         statement_id=statement.id,
                         rank=3),
    ]
    db.session.add_all(statement_problems)
    db.session.commit()

    yield statement

    for sp in statement_problems:
        db.session.delete(sp)
    db.session.commit()

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
def comments(app, users, authorized_user) -> List[dict]:
    author = users[-1]  # should not be the same as current authorized user

    comments_ = [
        Comment(
            comment=f'Comment for py_run_id #{py_run_id}',
            py_run_id=py_run_id,
            user_id=authorized_user.user['id'],
            author_user_id=author['id']
        ) for py_run_id in range(1, 4)
    ]

    db.session.add_all(comments_)
    db.session.commit()

    yield comments_

    db.session.query(Comment).delete()
    db.session.commit()


@pytest.yield_fixture
def comment(comments) -> dict:
    yield comments[0]


@pytest.yield_fixture
def group(app, users):
    group = Group(name='Групповые')
    db.session.add(group)
    db.session.flush()

    user_ids = [user['id'] for user in users]

    user_groups = [UserGroup(user_id=user_id, group_id=group.id)
                   for user_id in user_ids]
    db.session.add_all(user_groups)

    db.session.commit()

    yield group

    for u_g in user_groups:
        db.session.delete(u_g)

    db.session.delete(group)

    db.session.commit()
