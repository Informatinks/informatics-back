import io
from unittest.mock import patch

import pytest
from flask import url_for, g

from informatics_front.view.course.contest.problem import check_contest_connection

DEFAULT_PAGE = 1
DEFAULT_COUNT = 10


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
@patch('informatics_front.view.course.contest.problem.EjudgeProblem.generate_samples_json')
def test_problem(generate_samples_json, client, contest_connection):
    problem = contest_connection.contest.statement.problems[0]
    url = url_for('contest.problem',
                  contest_id=contest_connection.contest_id,
                  problem_id=problem.id)
    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert content.get('id') == problem.id

    generate_samples_json.assert_called()

    for field in ('content', 'description', 'memorylimit', 'name', 'output_only', 'timelimit', 'sample_tests_json'):
        assert getattr(problem, field) == content.get(field, -1)  # avoid None is None comparison


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
def test_problem_without_connection(client, problem, ongoing_workshop):
    contest = ongoing_workshop['contest']
    url = url_for('contest.problem',
                  contest_id=contest.id,
                  problem_id=problem.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
def test_check_contest_connection(contest_connection):
    check_contest_connection(contest_connection.contest_id, error_obj=ValueError())


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
def test_check_contest_connection_without_conn():
    with pytest.raises(ValueError):
        check_contest_connection(contest_id=12345, error_obj=ValueError())


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
def test_get_problem_submission(client, problem):
    CONTEST_ID = 12335
    user_id = g.user['id']
    url = url_for('contest.submissions', contest_id=CONTEST_ID,
                  problem_id=problem.id, page=DEFAULT_PAGE, )

    with patch('informatics_front.plugins.internal_rmatics.get_runs_filter') as get_runs_filter:
        get_runs_filter.return_value = ({}, 200)
        with patch('informatics_front.view.course.contest.problem.check_contest_connection') as mock_check_conn:
            resp = client.get(url)

    assert resp.status_code == 200
    get_runs_filter.assert_called_with(problem.id, CONTEST_ID, {'page': DEFAULT_PAGE,
                                                                'user_id': user_id,
                                                                'count': DEFAULT_COUNT})
    mock_check_conn.assert_called_once()


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
def test_send_submission(client, problem, contest_connection):
    data = {
        'lang_id': 2,
        'file': (io.BytesIO(b'sample data'), 'test.cpp',)
    }
    url = url_for('contest.submissions', problem_id=problem.id, contest_id=contest_connection.contest_id)
    with patch('informatics_front.plugins.internal_rmatics.send_submit') as send_submit:
        send_submit.return_value = ({}, 200)
        with patch('informatics_front.view.course.contest.problem.check_contest_connection') as mock_check_conn:
            resp = client.post(url, data=data, content_type='multipart/form-data')

    assert resp.status_code == 200
    mock_check_conn.assert_called_once()
    send_submit.assert_called_once()


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
def test_send_submission_without_file(client, problem, contest_connection):
    data = {
        'lang_id': 2,
    }
    url = url_for('contest.submissions', problem_id=problem.id, contest_id=contest_connection.contest_id)
    resp = client.post(url, data=data, content_type='multipart/form-data')
    assert resp.status_code == 400
