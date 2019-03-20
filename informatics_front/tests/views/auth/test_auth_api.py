from collections import namedtuple
from time import sleep
from unittest import mock

import pytest
from flask import url_for, g

from informatics_front import User, db
from informatics_front.model.refresh_tokens import RefreshToken
from informatics_front.plugins import tokenizer
from informatics_front.utils.tokenizer.handlers import map_action_routes
from informatics_front.view.auth.authorization import PasswordChangeApi

NEW_PASSWORD = 'new-password'
ACTIONS_URL_MOUNTPOINT = 'foo'
CHANGE_ACTION_ROUTE_NAME = 'bar'
SECRET_KEY = 'foo'
USER_EMAIL = 'user@example.com'
RESET_TOKEN = 'baz'


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


@pytest.mark.auth
def test_password_reset_invalid_payload(client, users):
    """Test password change link is not send if payload is invalid
    """
    with mock.patch('informatics_front.view.auth.authorization.gmail') as gmail, \
            mock.patch('informatics_front.view.auth.authorization.Message') as Message, \
            mock.patch('informatics_front.view.auth.authorization.tokenizer') as tokenizer:
        user = users[-1]
        url = url_for('auth.reset')

        # reset with well-signed, but insufficient payload
        resp = client.post(url, data={})
        assert resp.status_code == 400
        gmail.send.assert_not_called()

        gmail.reset_mock()
        Message.reset_mock()

        # reset pass for user with no email
        data = {
            'username': user.get('user_name')
        }
        resp = client.post(url, data=data)
        assert resp.status_code == 400
        gmail.send.assert_not_called()



@pytest.mark.auth
def test_password_reset_valid_payload(client, users):
    """Test password change link is sent with generated valid token to user
    """
    with mock.patch('informatics_front.view.auth.authorization.gmail') as gmail, \
            mock.patch('informatics_front.view.auth.authorization.Message') as Message, \
            mock.patch('informatics_front.view.auth.authorization.tokenizer') as tokenizer:
        user = users[-1]
        url = url_for('auth.reset')
        tokenizer.pack.return_value = RESET_TOKEN

        # set email for user
        db.session.query(User). \
            filter(User.id == user['id']). \
            update({'email': USER_EMAIL})
        db.session.commit()

        # reset by username
        data = {
            'username': user.get('user_name')
        }
        resp = client.post(url, data=data)
        assert resp.status_code == 200

        message_text = Message.call_args[1]['text']
        assert RESET_TOKEN in message_text
        gmail.send.assert_called()

        gmail.reset_mock()
        Message.reset_mock()

        # reset by email
        data = {
            'email': USER_EMAIL,
        }
        resp = client.post(url, data=data)
        assert resp.status_code == 200

        message_text = Message.call_args[1]['text']
        assert RESET_TOKEN in message_text
        gmail.send.assert_called()


@pytest.mark.auth
def test_password_change(client, app, users):
    """Test ...
    """
    user = users[0]

    # FIXME: switch to local_app to prevent blueprint confusing
    reset_action_mountpoint = f'{ACTIONS_URL_MOUNTPOINT}_reset'
    reset_action_route_name = f'{CHANGE_ACTION_ROUTE_NAME}_reset'

    # register password change action to app
    map_action_routes(app, (
        (reset_action_route_name, PasswordChangeApi.as_view(reset_action_route_name), 86000),
    ), reset_action_mountpoint)

    # generate valid reset token
    payload = {
        'user_id': user.get('id')
    }
    token = tokenizer.pack(payload)

    # generate password hash
    new_password_hash = User.hash_password(NEW_PASSWORD)

    # request password change
    url = url_for(f'{reset_action_mountpoint}.{reset_action_route_name}', token=token)
    resp = client.post(url, data={
        'password': NEW_PASSWORD,
    })

    # ensure password is changed
    user = db.session.query(User). \
        filter_by(id=user['id']). \
        one_or_none()

    assert new_password_hash == user.password_md5
