import pytest

from unittest import mock

from flask import g
from werkzeug.exceptions import Unauthorized

from informatics_front.utils.auth import authenticate
from informatics_front.utils.auth.make_jwt import decode_jwt_token


@pytest.mark.auth
def test_decode_valid_token(token: str):
    result = decode_jwt_token(token)

    assert result is not None
    assert 'id' in result
    assert 'roles' in result


@pytest.mark.auth
def test_decode_expired_token(expired_token: str):
    result = decode_jwt_token(expired_token)

    assert result is None


@pytest.mark.auth
def test_auth_by_token(token):
    with mock.patch('informatics_front.utils.auth.request') as request:
        request.headers = {
            'Authorization': f'JWT {token}'
        }
        authenticate()
    assert g.user is not None
    assert 'id' in g.user


@pytest.mark.auth
def test_auth_by_expired_token(expired_token: str):
    with mock.patch('informatics_front.utils.auth.request') as request:
        request.headers = {
            'Authorization': f'JWT {expired_token}'
        }
        with pytest.raises(Unauthorized):
            authenticate()
