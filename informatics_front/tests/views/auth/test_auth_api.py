import pytest

from time import sleep
from collections import namedtuple

from flask import url_for, g

from informatics_front import User, db
from informatics_front.model.refresh_tokens import RefreshToken


@pytest.mark.auth
def test_refresh_token(client, user_with_token):
    url = url_for('auth.refresh')
    token = user_with_token.get('token')
    resp = client.post(url, data={'refresh_token': token})

    assert resp.status_code == 200

    assert 'data' in resp.json

    content = resp.json['data']

    user: User = user_with_token['user']
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
        .filter(RefreshToken.user_id == user['id']) \
        .one_or_none()

    assert rt is not None


@pytest.mark.auth
def test_signout(client, users):
    login_url = url_for('auth.login')
    logout_url = url_for('auth.logout')
    TokensContainer = namedtuple('TokensContainer', ['token', 'refresh_token'])

    # get user
    user = users[0]
    auth_credentials = {
        'username': user.get('user_name'),
        'password': user.get('password'),
    }

    # auth user twice and store tokens
    token_containers = []
    for i in range(0, 2):
        resp = client.post(login_url, data=auth_credentials)
        assert resp.status_code == 200

        content = resp.json
        assert 'data' in content

        content = content['data']
        assert 'token' in content
        assert 'refresh_token' in content

        token_containers.append(TokensContainer(token=content.get('token'),
                                                refresh_token=content.get('refresh_token')))

        sleep(1)  # prevent getting same token based on current timestamp

    # ensure recieved tokens are unique
    assert token_containers[0].token != token_containers[1].token
    assert token_containers[0].refresh_token != token_containers[1].refresh_token

    # mock: set user id into session,
    g.user = {'id': user.get('id')}

    # 422 if no refesh_token provided
    resp = client.post(logout_url)
    assert resp.status_code == 422

    # logout first token
    resp = client.post(logout_url, data={
        'refresh_token': token_containers[0].refresh_token
    })
    assert resp.status_code == 200

    # ensure first logged out, second — not
    assert db.session.query(RefreshToken).filter_by(user_id=user['id']).count() == 1

    # logout second session
    resp = client.post(logout_url, data={
        'refresh_token': token_containers[1].refresh_token
    })

    # ensure second logged out
    assert db.session.query(RefreshToken).filter_by(user_id=user['id']).count() == 0
