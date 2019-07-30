from flask import url_for, g

from informatics_front.model import db
from informatics_front.model.workshop.workshop_connection import WorkshopConnection
from informatics_front.utils.enums import WorkshopConnectionStatus

WORKSHOP_ACCESS_TOKEN = 'foo'
WORKSHOP_INVALID_ACCESS_TOKEN = 'invalid-token'


def test_reject_join_workshop_if_token_invalid(client, authorized_user, empty_workshop):
    url = url_for('workshop.join', workshop_id=empty_workshop.id, token=WORKSHOP_INVALID_ACCESS_TOKEN)
    resp = client.post(url)
    assert resp.status_code == 404, 'should return 404 if access token is invalid or not found'

    user_id = g.user['id']
    workshop_connection = db.session.query(WorkshopConnection) \
        .filter(WorkshopConnection.user_id == user_id) \
        .filter(WorkshopConnection.workshop_id == empty_workshop.id) \
        .one_or_none()

    assert workshop_connection is None, 'should not create connection if access token is invalid'


def test_apply_join_workshop_if_token_valid(client, authorized_user, empty_workshop):
    url = url_for('workshop.join', workshop_id=empty_workshop.id, token=WORKSHOP_ACCESS_TOKEN)
    resp = client.post(url)
    assert resp.status_code == 200, 'should return 200 if access token is valid'

    user_id = g.user['id']
    workshop_connection = db.session.query(WorkshopConnection) \
        .filter(WorkshopConnection.user_id == user_id) \
        .filter(WorkshopConnection.workshop_id == empty_workshop.id) \
        .one_or_none()

    assert workshop_connection is not None, 'should create connection if access token is valid'


def test_join_workshop_returns_connection(client, authorized_user, empty_workshop):
    url = url_for('workshop.join', workshop_id=empty_workshop.id, token=WORKSHOP_ACCESS_TOKEN)
    resp = client.post(url)
    assert resp.status_code == 200, 'should return 200 if access token is valid'

    content = resp.json
    assert 'data' in content

    content = content['data']
    for field in ('id', 'status', 'user_id', 'workshop_id'):
        assert field in content, 'reponse should have connection fields'

    assert content.get('workshop_id') == empty_workshop.id, 'connection should point to correct workshop'
    assert content.get('user_id') == g.user['id'], 'connection should point to correct user'
    assert content.get(
        'status') == WorkshopConnectionStatus.APPLIED.name, 'connection should be created in APPLIED status'


def test_repeated_join_returns_existing_connection(client, authorized_user, empty_workshop):
    url = url_for('workshop.join', workshop_id=empty_workshop.id, token=WORKSHOP_ACCESS_TOKEN)
    resp = client.post(url)
    assert resp.status_code == 200, 'should return 200 if access token is valid'

    content = resp.json
    assert 'data' in content

    response_connection1 = content['data']
    for field in ('id', 'status', 'user_id', 'workshop_id'):
        assert field in response_connection1, 'reponse should have connection fields'

    resp = client.post(url)
    assert resp.status_code == 200, 'should return 200 if access token is valid'
    content = resp.json
    assert 'data' in content

    response_connection2 = content['data']
    assert response_connection1 == response_connection2, 'should return same connection object for repeated request'
