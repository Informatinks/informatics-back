import pytest

from informatics_front import Problem, CourseModule, Statement, db
from informatics_front.model import StatementProblem

VALID_TIME = 100500
COURSE_VISIBLE = 1


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
