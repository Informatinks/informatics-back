import io
from unittest.mock import patch

import pytest
from flask import url_for, g
from werkzeug.exceptions import Forbidden

from informatics_front.view.course.contest.problem import check_contest_availability, check_contest_languages

DEFAULT_PAGE = 1
DEFAULT_COUNT = 10
DEFAULT_CONTEST_ID = 10


def test_check_contest_languages_non_aware(contest_connection):
    contest = contest_connection.contest
    try:
        language_id = 999
        check_contest_languages(contest, language_id, Exception)
    except Exception as exc:
        pytest.fail('Should allow submision on any lang '
                    'if contest is not language aware')


def test_check_contest_languages_permitted(contest_builder, languages):
    contest_languages = languages[0:3]
    contest = contest_builder(languages=contest_languages)

    for contest_language in contest_languages:
        try:
            check_contest_languages(contest, contest_language.code, Exception)
        except Exception as exc:
            pytest.fail('Should allow submision on permitted lang')


def test_check_contest_languages_prohibited(contest_builder, languages):
    contest_languages = languages[0:3]
    contest = contest_builder(languages=contest_languages)

    with pytest.raises(Exception):
        check_contest_languages(contest, languages[3].code, Exception)


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
    check_contest_availability(contest_connection.contest_id, error_obj=ValueError())


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
def test_check_contest_connection_without_conn():
    with pytest.raises(ValueError):
        check_contest_availability(contest_id=12345, error_obj=ValueError())


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
@patch('informatics_front.plugins.internal_rmatics.get_runs_filter')
@patch('informatics_front.view.course.contest.problem.check_contest_availability')
def test_get_problem_submission(mock_check_avail, get_runs_filter, client, problem):
    user_id = g.user['id']
    url = url_for('contest.submissions', contest_id=DEFAULT_CONTEST_ID,
                  problem_id=problem.id, page=DEFAULT_PAGE, )

    get_runs_filter.return_value = ({}, 200)
    resp = client.get(url)

    assert resp.status_code == 200
    get_runs_filter.assert_called_with(problem.id, DEFAULT_CONTEST_ID, {'page': DEFAULT_PAGE,
                                                                        'user_id': user_id,
                                                                        'count': DEFAULT_COUNT})
    mock_check_avail.assert_called_once()


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
@patch('informatics_front.plugins.internal_rmatics.send_submit')
@patch('informatics_front.view.course.contest.problem.check_contest_availability')
def test_send_submission(mock_check_avail, mock_send_submit, client, problem, contest_connection):
    mock_check_avail.return_value = contest_connection
    mock_send_submit.return_value = ({}, 200)

    data = {
        'lang_id': 2,
        'file': (io.BytesIO(b'sample data'), 'test.cpp',)
    }
    url = url_for('contest.submissions', problem_id=problem.id, contest_id=contest_connection.contest_id)
    resp = client.post(url, data=data, content_type='multipart/form-data')

    assert resp.status_code == 200
    mock_check_avail.assert_called_once()
    mock_send_submit.assert_called_once()


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
def test_send_submission_without_file(client, problem, contest_connection):
    data = {
        'lang_id': 2,
    }
    url = url_for('contest.submissions', problem_id=problem.id, contest_id=contest_connection.contest_id)
    resp = client.post(url, data=data, content_type='multipart/form-data')
    assert resp.status_code == 400


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
@patch('informatics_front.view.course.contest.problem.internal_rmatics.send_submit')
@patch('informatics_front.view.course.contest.problem.check_contest_availability')
@patch('informatics_front.view.course.contest.problem.check_contest_languages')
def test_send_submission_with_permitted_lang(mock_check_langs, mock_check_avail, mock_send_submit,
                                             client, problem, contest_connection, languages):
    mock_send_submit.return_value = (None, 200)

    data = {
        'lang_id': 999,
        'file': (io.BytesIO(b'sample data'), 'test.cpp',)
    }

    url = url_for('contest.submissions', problem_id=problem.id, contest_id=contest_connection.contest_id)
    resp = client.post(url, data=data, content_type='multipart/form-data')

    assert resp.status_code == 200
    mock_check_langs.assert_called()
    mock_check_avail.assert_called()
    mock_send_submit.assert_called()


@pytest.mark.problem
@pytest.mark.usefixtures('authorized_user')
@patch('informatics_front.view.course.contest.problem.internal_rmatics.send_submit')
@patch('informatics_front.view.course.contest.problem.check_contest_availability')
@patch('informatics_front.view.course.contest.problem.check_contest_languages')
def test_send_submission_with_prohibited_lang(mock_check_langs, mock_check_avail, mock_send_submit,
                                              client, problem, contest_connection, languages):
    mock_check_langs.side_effect = Forbidden

    data = {
        'lang_id': 999,
        'file': (io.BytesIO(b'sample data'), 'test.cpp',)
    }

    url = url_for('contest.submissions', problem_id=problem.id, contest_id=contest_connection.contest_id)
    resp = client.post(url, data=data, content_type='multipart/form-data')

    assert resp.status_code == 403
    mock_check_langs.assert_called()
    mock_check_avail.assert_called()
    mock_send_submit.assert_not_called()
