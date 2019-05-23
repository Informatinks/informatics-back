from flask import url_for, g

from informatics_front.model import db
from informatics_front.model.workshop.workshop_connection import WorkshopConnection

WORKSHOP_ACCESS_TOKEN = 'foo'
WORKSHOP_INVALID_ACCESS_TOKEN = 'invalid-token'


def test_reject_join_workshop_if_no_token_provided(client, authorized_user, empty_workshop):
    url = url_for('workshop.join', workshop_id=empty_workshop.id)
    resp = client.get(url)
    assert resp.status_code == 400, 'should return 400 if no access token provided'

    user_id = g.user['id']
    workshop_connection = db.session.query(WorkshopConnection) \
        .filter(WorkshopConnection.user_id == user_id) \
        .filter(WorkshopConnection.workshop_id == empty_workshop.id) \
        .one_or_none()

    assert workshop_connection is None, 'should not create connection if no access token provided'


def test_reject_join_workshop_if_token_invalid(client, authorized_user, empty_workshop):
    url = url_for('workshop.join', workshop_id=empty_workshop.id, token=WORKSHOP_INVALID_ACCESS_TOKEN)
    resp = client.get(url)
    assert resp.status_code == 400, 'should return 400 if access token is invalid'

    user_id = g.user['id']
    workshop_connection = db.session.query(WorkshopConnection) \
        .filter(WorkshopConnection.user_id == user_id) \
        .filter(WorkshopConnection.workshop_id == empty_workshop.id) \
        .one_or_none()

    assert workshop_connection is None, 'should not create connection if access token is invalid'


def test_apply_join_workshop_if_token_valid(client, authorized_user, empty_workshop):
    url = url_for('workshop.join', workshop_id=empty_workshop.id, token=WORKSHOP_ACCESS_TOKEN)
    resp = client.get(url)
    assert resp.status_code == 200, 'should return 200 if access token is valid'

    user_id = g.user['id']
    workshop_connection = db.session.query(WorkshopConnection) \
        .filter(WorkshopConnection.user_id == user_id) \
        .filter(WorkshopConnection.workshop_id == empty_workshop.id) \
        .one_or_none()

    assert workshop_connection is not None, 'should create connection if access token is valid'
