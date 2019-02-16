import hashlib
from typing import List

import pytest

from informatics_front import User, db
from informatics_front.model.refresh_tokens import RefreshToken
from informatics_front.utils.auth.make_jwt import generate_refresh_token


@pytest.fixture()
def users() -> List[dict]:
    password = 'simple_pass'
    password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    users = [
        User(username=f'user{i}', password_md5=password_hash) for i in range(1, 3)
    ]
    db.session.add_all(users)
    db.session.flush()

    users = [
        {'user_name': user.username,
         'id': user.id,
         'password': password} for user in users
    ]

    db.session.commit()

    return users


@pytest.fixture()
def authorized_user(users) -> dict:
    user_id = users[0]['id']
    user = db.session.query(User).get(user_id)
    token = generate_refresh_token(user)

    rt = RefreshToken(token=token, user_id=user_id)

    db.session.add(rt)
    db.session.commit()

    return {'user': user, 'token': token}
