import pytest

from informatics_front import Problem, CourseModule, Statement, db
from informatics_front.model import StatementProblem
from informatics_front.model.problem import EjudgeProblem

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
def course_module(app) -> dict:
    ejudge_problems = [
        EjudgeProblem.create(
            ejudge_prid=1,
            contest_id=1,
            ejudge_contest_id=1,
            problem_id=1,
        ),
        EjudgeProblem.create(
            ejudge_prid=2,
            contest_id=2,
            ejudge_contest_id=1,
            problem_id=2,
        ),
        EjudgeProblem.create(
            ejudge_prid=3,
            contest_id=3,
            ejudge_contest_id=2,
            problem_id=1,
        )
    ]
    db.session.add_all(ejudge_problems)
    db.session.flush(ejudge_problems)
    problems = [
        Problem(name='Problem1', pr_id=ejudge_problems[0].id),
        Problem(name='Problem2', pr_id=ejudge_problems[1].id),
        Problem(name='Problem3', pr_id=ejudge_problems[2].id),
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
    db.session.flush()

    course_module = CourseModule(instance_id=statement.id, module=Statement.MODULE, visible=COURSE_VISIBLE, )
    db.session.add(course_module)
    db.session.commit()

    yield course_module

    for sp in statement_problems:
        db.session.delete(sp)
    db.session.commit()

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
