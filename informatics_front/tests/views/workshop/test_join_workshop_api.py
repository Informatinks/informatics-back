from flask import url_for, g

from informatics_front import db
from informatics_front.model.workshop.workshop_connection import WorkshopConnection


def test_join_workshop(client, authorized_user, empty_workshop):
    url = url_for('workshop.join', workshop_id=empty_workshop.id)
    resp = client.post(url)
    assert resp.status_code == 200

    user_id = g.user['id']
    workshop_connection = db.session.query(WorkshopConnection) \
                                    .filter(WorkshopConnection.user_id == user_id) \
                                    .filter(WorkshopConnection.workshop_id == empty_workshop.id)\
                                    .one_or_none()

    assert workshop_connection is not None
