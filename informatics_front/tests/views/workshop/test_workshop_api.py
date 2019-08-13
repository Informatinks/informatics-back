import pytest
import sqlalchemy
from flask import url_for

from informatics_front.model import db
from informatics_front.utils.enums import WorkshopConnectionStatus

NON_EXISTING_WORKSHOP_ID = -1


class DBStatementCounter(object):
    """
    
    Count the number of execute()'s performed against the given sqlalchemy connection.
    Use as a context manager.    

    Usage:
        with DBStatementCounter(conn) as ctr:
            conn.execute("SELECT 1")
            conn.execute("SELECT 1")
        assert ctr.get_count() == 2
    """

    def __init__(self, conn):
        self.conn = conn
        self.count = 0
        # Will have to rely on this since sqlalchemy 0.8 does not support
        # removing event listeners
        self.do_count = False
        sqlalchemy.event.listen(conn, 'after_execute', self.callback)

    def __enter__(self):
        self.do_count = True
        return self

    def __exit__(self, *_):
        self.do_count = False

    def get_count(self):
        return self.count

    def callback(self, *_):
        if self.do_count:
            self.count += 1


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_non_existing_workshop(client):
    url = url_for('workshop.read', workshop_id=NON_EXISTING_WORKSHOP_ID)
    resp = client.get(url)
    assert resp.status_code == 404
    content = resp.json

    assert 'status' in content
    assert content['status'] == 'error'


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_accepted_workshop(client, workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.ACCEPTED)
    url = url_for('workshop.read', workshop_id=workshop_connection.workshop.id)
    resp = client.get(url)
    assert resp.status_code == 200
    content = resp.json

    assert 'status' in content
    assert content['status'] == 'success'

    assert 'data' in content
    data = content['data']
    assert data['id'] == workshop_connection.workshop.id


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_applied_workshop(client, workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.APPLIED)
    url = url_for('workshop.read', workshop_id=workshop_connection.workshop.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_disqualified_workshop(client, workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.DISQUALIFIED)
    url = url_for('workshop.read', workshop_id=workshop_connection.workshop.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_rejected_workshop(client, workshop_connection_builder):
    workshop_conn = workshop_connection_builder(WorkshopConnectionStatus.REJECTED)
    url = url_for('workshop.read', workshop_id=workshop_conn.workshop.id)
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_promoted_workshop(client, workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.PROMOTED)
    url = url_for('workshop.read', workshop_id=workshop_connection.workshop.id)
    resp = client.get(url)
    assert resp.status_code == 200
    content = resp.json

    assert 'status' in content
    assert content['status'] == 'success'

    assert 'data' in content
    data = content['data']
    assert data['id'] == workshop_connection.workshop.id

    assert 'contests' in data
    assert len(data.get('contests')) == 1


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_read_draft_workshop(client, draft_workshop_connection):
    url = url_for('workshop.read', workshop_id=draft_workshop_connection.workshop.id)

    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_workshop_has_contests(client, workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.ACCEPTED)
    workshop = workshop_connection.workshop
    url = url_for('workshop.read', workshop_id=workshop.id)
    resp = client.get(url)
    assert resp.status_code == 200
    content = resp.json

    assert 'status' in content
    assert content['status'] == 'success'

    assert 'data' in content
    data = content['data']
    assert all(k in data for k in ('id', 'name', 'visibility', 'contests'))
    assert data['id'] == workshop.id
    assert len(data['contests']) == 1


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_workshop_contest_has_valid_statement(client, workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.ACCEPTED)
    workshop = workshop_connection.workshop
    url = url_for('workshop.read', workshop_id=workshop.id)
    resp = client.get(url)
    assert resp.status_code == 200
    content = resp.json

    # check required fields in nested schemas
    contest = content['data']['contests'][0]
    assert all(k in contest for k in ('id', 'position', 'statement'))

    statement = contest['statement']
    assert all(k in statement for k in ('id', 'name', 'summary'))


@pytest.mark.workshop
@pytest.mark.usefixtures('authorized_user')
def test_workshop_not_produce_n1(client, workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.ACCEPTED)
    workshop = workshop_connection.workshop
    url = url_for('workshop.read', workshop_id=workshop.id)

    with DBStatementCounter(db.engine) as ctr:
        resp = client.get(url)

    assert resp.status_code == 200
    # First for workshop.
    # Second for languages, if no contest.languages specified
    assert ctr.get_count() == 2, 'should produce no more than two SQL requests to prevent N+1'
