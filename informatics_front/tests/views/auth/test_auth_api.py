import pytest
from flask import url_for

from informatics_front import User, db
from informatics_front.model.refresh_tokens import RefreshToken


@pytest.mark.auth
def test_refresh_token(client, authorized_user):
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


@pytest.mark.auth
def test_signin(client, users):
    url = url_for('auth.login')
    user = users[0]

    auth_credentials = {
        'username': user['user_name'],
        'password': user['password'],
    }

    resp = client.post(url, data=auth_credentials)

    assert resp.status_code == 200

    content = resp.json

    assert 'data' in content

    content = content['data']

    assert 'token' in content
    assert 'refresh_token' in content

    token = content['refresh_token']

    rt = db.session.query(RefreshToken) \
        .filter(RefreshToken.token == token) \
        .filter(RefreshToken.user_id == user['id'])\
        .one_or_none()

    assert rt is not None
