import pytest
from flask import url_for

from informatics_front import User


@pytest.mark.auth
def test_authorized_user(client, authorized_user):
    url = url_for('auth.refresh')
    token = authorized_user.get('token')
    resp = client.post(url, data={'refresh_token': token})

    assert resp.status_code == 200

    assert 'data' in resp.json

    content = resp.json['data']

    user: User = authorized_user['user']
    assert content.get('id') == user.id
    assert content.get('username') == user.username
    assert 'token' in content
    assert 'refresh_token' not in content
