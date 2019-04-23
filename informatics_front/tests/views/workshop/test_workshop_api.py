import pytest
from flask import url_for

NON_EXISTING_WORKSHOP_ID = -1


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_non_existing_workshop(client, ):
    url = url_for('workshop.read', workshop_id=NON_EXISTING_WORKSHOP_ID)
    resp = client.get(url)
    assert resp.status_code == 404
    content = resp.json

    assert 'status' in content
    assert content['status'] == 'error'


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_accepted_workshop(client, accepted_workshop_connection):
    url = url_for('workshop.read', workshop_id=accepted_workshop_connection.workshop.id)
    resp = client.get(url)
    assert resp.status_code == 200
    content = resp.json

    assert 'status' in content
    assert content['status'] == 'success'

    assert 'data' in content
    data = content['data']
    assert data['id'] == accepted_workshop_connection.workshop.id


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_applied_workshop(client, applied_workshop_connection):
    url = url_for('workshop.read', workshop_id=applied_workshop_connection.workshop.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_disqualified_workshop(client, disqualified_workshop_connection):
    url = url_for('workshop.read', workshop_id=disqualified_workshop_connection.workshop.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_rejected_workshop(client, rejected_workshop_connection):
    url = url_for('workshop.read', workshop_id=rejected_workshop_connection.workshop.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_draft_workshop(client, draft_workshop_connection):
    url = url_for('workshop.read', workshop_id=draft_workshop_connection.workshop.id)

    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_workshop_has_contests(client, accepted_workshop_connection):
    workshop = accepted_workshop_connection.workshop
    url = url_for('workshop.read', workshop_id=workshop.id)
    resp = client.get(url)
    assert resp.status_code == 200
    content = resp.json

    assert 'status' in content
    assert content['status'] == 'success'

    assert 'data' in content
    data = content['data']
    assert data['id'] == workshop.id

    assert 'contests' in data
    assert len(data['contests']) == 1


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_workshop_contest_has_valid_statement(client, accepted_workshop_connection):
    workshop = accepted_workshop_connection.workshop
    url = url_for('workshop.read', workshop_id=workshop.id)
    resp = client.get(url)
    assert resp.status_code == 200
    content = resp.json

    # check required fields in nested schemas
    contest = content['data']['contests'][0]
    assert all(k in contest for k in ('id', 'position', 'statement'))

    statement = contest['statement']
    assert all(k in statement for k in ('id', 'name', 'summary'))
