import pytest

from typing import List

from informatics_front import Comment, db


@pytest.yield_fixture
def comments(app, users, authorized_user) -> List[dict]:
    author = users[-1]  # should not be the same as current authorized user

    comments_ = [
        Comment(
            comment=f'Comment for py_run_id #{py_run_id}',
            py_run_id=py_run_id,
            user_id=authorized_user.user['id'],
            author_user_id=author['id']
        ) for py_run_id in range(1, 4)
    ]

    db.session.add_all(comments_)
    db.session.commit()

    yield comments_

    db.session.query(Comment).delete()
    db.session.commit()


@pytest.yield_fixture
def comment(comments) -> dict:
    yield comments[0]
