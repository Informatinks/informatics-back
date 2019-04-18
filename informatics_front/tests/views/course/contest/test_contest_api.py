import pytest

from flask import url_for, g
from werkzeug.exceptions import NotFound

from informatics_front import db
from informatics_front.model.workshop.contest_connection import ContestConnection
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
@pytest.mark.usefixtures('authorized_user', 'applied_workshop_connection')
def test_check_workshop_permissions_with_applied_connection(ongoing_workshop):
    user_id = g.user['id']
    w = ongoing_workshop['workshop']
    with pytest.raises(NotFound):
        ContestApi._check_workshop_permissions(user_id, w)


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user')
def test_check_workshop_permissions_with_accepted_connection(ongoing_workshop, accepted_workshop_connection):
    user_id = g.user['id']
    w = ongoing_workshop['workshop']
    ret_con = ContestApi._check_workshop_permissions(user_id, w)
    assert ret_con.id == accepted_workshop_connection.id


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user')
def test_create_contest_connection_when_not_exists(ongoing_workshop):
    contest = ongoing_workshop['contest_instance']
    user_id = g.user['id']
    cc = ContestApi._create_contest_connection(user_id, contest.id)
    assert cc is not None
    try:
        assert db.session.query(ContestConnection) \
            .filter_by(user_id=user_id, contest_instance_id=contest.id).one_or_none()
    finally:
        # we wont to check object creation so we have to clear after that
        db.session.delete(cc)
        db.session.commit()


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user')
def test_create_contest_connection_when_exists(ongoing_workshop, contest_connection):
    contest = ongoing_workshop['contest_instance']
    user_id = g.user['id']
    cc = ContestApi._create_contest_connection(user_id, contest.id)
    assert cc is not None
    assert cc.id == contest_connection.id


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user', 'statement', 'accepted_workshop_connection')
def test_contest_api(client, ongoing_workshop):

    contest = ongoing_workshop['contest_instance']

    url = url_for('contest.contest', contest_instance_id=contest.id)
    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert 'created_at' in content

    contest_instance_resp = content['contest_instance']
    assert contest_instance_resp.get('id') == contest.id
    contest_resp = contest_instance_resp['contest']

    assert contest_resp.get('id') == contest.contest.id


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user', 'statement', 'accepted_workshop_connection')
def test_contest_api_not_exists(client):
    url = url_for('contest.contest', contest_instance_id=NON_EXISTING_ID)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.contest_problem
@pytest.mark.usefixtures('authorized_user')
def test_contest_api_if_workshop_connection_not_exist(client, ongoing_workshop):
    contest = ongoing_workshop['contest_instance']

    url = url_for('contest.contest', contest_instance_id=contest.id)
    resp = client.get(url)
    assert resp.status_code == 404
