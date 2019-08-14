from unittest.mock import patch

import pytest
from flask import url_for, g
from werkzeug.exceptions import NotFound

from informatics_front.model import db
from informatics_front.utils.enums import WorkshopConnectionStatus
from informatics_front.view.course.contest.contest import ContestApi

NON_EXISTING_ID = -1


@pytest.mark.contest_problem
def test_contest_load_problem(statement):
    problems = ContestApi._load_problems(statement.id)
    assert len(problems) == 3


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user')
def test_check_workshop_permissions_without_connection(ongoing_workshop):
    user_id = g.user['id']
    w = ongoing_workshop['workshop']
    with pytest.raises(NotFound):
        ContestApi._check_workshop_permissions(user_id, w)


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user')
def test_check_workshop_permissions_with_applied_connection(workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.APPLIED)
    user_id = g.user['id']
    with pytest.raises(NotFound):
        ContestApi._check_workshop_permissions(user_id, workshop_connection.workshop)


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user')
def test_check_workshop_permissions_with_accepted_connection(ongoing_workshop, workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.ACCEPTED)
    user_id = g.user['id']
    w = ongoing_workshop['workshop']
    ret_con = ContestApi._check_workshop_permissions(user_id, w)
    assert ret_con.id == workshop_connection.id


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user', 'statement')
def test_contest_api(client, ongoing_workshop, workshop_connection_builder, languages):
    workshop_connection_builder(WorkshopConnectionStatus.ACCEPTED)

    contest = ongoing_workshop['contest']

    url = url_for('contest.contest', contest_id=contest.id)
    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert 'created_at' in content

    contest_resp = content['contest']
    assert contest_resp.get('id') == contest.id

    statement_resp = contest_resp['statement']
    assert statement_resp.get('id') == contest.statement.id

    # Test contest languages
    assert 'languages' in contest_resp, 'languages should persist in contests'

    serialized_languages = contest_resp.get('languages')
    assert len(serialized_languages) == 5, 'should return all languages ' \
                                           'if no languages specified for contest'

    # Ensure all languages persist with proper keys
    for language in languages:
        serialized_languages_ = [s_lang for s_lang in serialized_languages if language.id == s_lang.get('id')]
        assert serialized_languages_, f'contest should contain language {language.id}'

        serialized_language = serialized_languages_[0]
        for attr in ('id', 'code', 'title', 'mode'):
            assert attr in serialized_language, f'#{attr} should present in Language schema'

        assert serialized_language.get('code') == language.code
        assert serialized_language.get('title') == language.title
        assert serialized_language.get('mode') == language.mode


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user', 'statement')
def test_contest_api_not_exists(client, workshop_connection_builder):
    workshop_connection_builder(WorkshopConnectionStatus.APPLIED)
    url = url_for('contest.contest', contest_id=NON_EXISTING_ID)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user')
def test_contest_api_if_workshop_connection_not_exist(client, ongoing_workshop):
    contest = ongoing_workshop['contest']

    url = url_for('contest.contest', contest_id=contest.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user', 'statement')
@patch('informatics_front.view.course.contest.contest.ContestApi._check_workshop_permissions')
def test_contest_api_returns_correct_language_list(mock_check_ws_perms, client, contest_builder, languages):
    contest_languages = languages[0:3]
    contest = contest_builder(languages=contest_languages)

    url = url_for('contest.contest', contest_id=contest.id)
    resp = client.get(url)
    assert resp.status_code == 200

    # Ensure all languages persist with proper keys
    serialized_languages = resp.json['data']['contest']['languages']
    for language in contest_languages:
        serialized_languages_ = [s_lang for s_lang in serialized_languages if language.id == s_lang.get('id')]
        assert serialized_languages_, f'contest should contain language {language.id}'
