import io
from unittest.mock import patch, MagicMock
import pytest
from flask import url_for

DEFAULT_PAGE = 1
DEFAULT_COUNT = 10


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
def test_problem(client, problem, contest_connection):
    url = url_for('contest.problem',
                  contest_id=contest_connection.contest_id,
                  problem_id=problem.id)
    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert content.get('id') == problem.id

    for field in ('content', 'description', 'memorylimit', 'name', 'output_only', 'timelimit',):
        assert getattr(problem, field) == content.get(field, -1)  # avoid None is None comparison

#     Добавить ассерт на сэмплы


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
def test_get_problem_submission(client, authorized_user, problem):
    with patch('informatics_front.internal_rmatics.get_runs_filter') as get_runs_filter:
        get_runs_filter.return_value = ({}, 200)

        url = url_for('contest.submissions', problem_id=problem.id, page=DEFAULT_PAGE, )
        resp = client.get(url)
        assert resp.status_code == 200
        get_runs_filter.assert_called_with(problem.id, {'page': DEFAULT_PAGE,
                                                        'user_id': authorized_user.user['id'],
                                                        'count': DEFAULT_COUNT}, is_admin=False)


@pytest.mark.problem
def test_post_problem_submission(client, authorized_user, problem):
    with patch('informatics_front.internal_rmatics.send_submit') as send_submit:
        send_submit.return_value = ({}, 200)

        data = {
            'statement_id': 1,
            'lang_id': 2,
        }

        url = url_for('contest.submissions', problem_id=problem.id)
        data['file'] = io.BytesIO(b'sample data'), 'test.cpp'
        resp = client.post(url, data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        send_submit.reset_mock()

        # statement_id is an optional argument
        del data['statement_id']
        data['file'] = io.BytesIO(b'sample data'), 'test.cpp'
        url = url_for('contest.submissions', problem_id=problem.id)
        resp = client.post(url, data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        # send_submit.assert_called_with(True, g.user['id'], problem.id, None, 2)

        del data['file']
        resp = client.post(url, data=data, content_type='multipart/form-data')
        assert resp.status_code == 400
