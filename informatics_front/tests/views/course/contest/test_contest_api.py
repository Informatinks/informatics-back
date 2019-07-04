import pytest

from flask import url_for, g
from werkzeug.exceptions import NotFound

from informatics_front.model import db
from informatics_front.model.workshop.contest_connection import ContestConnection
from informatics_front.utils.enums import WorkshopConnectionStatus, WorkshopStatus
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
def test_contest_api(client, ongoing_workshop, workshop_connection_builder):
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
    contest_resp = contest_resp['statement']

    assert contest_resp.get('id') == contest.statement.id


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
