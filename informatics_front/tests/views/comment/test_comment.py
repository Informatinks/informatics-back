import pytest

from flask import g, url_for

NON_EXISTING_USER = -1
NON_EXISTING_RUN = 1337
INVALID_RUN = -1


@pytest.mark.comment
def test_get_comments(client, users, authorized_user, comments):
    """Ensure for every run for current authorized user
       we've got exactly one particular comment"""
    for comment in comments:
        py_run_id = comment.py_run_id
        url = url_for('comment.comment', run_id=py_run_id)

        resp = client.get(url)
        assert resp.status_code == 200

        content = resp.json
        assert 'data' in content

        content = content['data']
        assert len(content) == 1

        recieved_comment = content[0]
        assert recieved_comment['run_id'] == py_run_id

        for field in ('id', 'comment',):
            assert getattr(comment, field) == recieved_comment.get(field, -1)  # avoid None is None comparison

        # comment should have valid author
        author = users[-1]
        recieved_author = recieved_comment['author_user']
        assert recieved_author['id'] == author['id']


@pytest.mark.comment
def test_get_comments_for_invalid_user(client, authorized_user, comment):
    """Ensure invalid user in context returns 0 comments"""
    g.user['id'] = NON_EXISTING_USER
    url = url_for('comment.comment', run_id=comment.py_run_id)

    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert len(content) == 0


@pytest.mark.comment
def test_get_comments_for_invalid_run(client, authorized_user):
    """Ensure invalid run_id returns 0 comments"""
    url = url_for('comment.comment', run_id=NON_EXISTING_RUN)

    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert len(content) == 0

    # for non-integer run should return 404, defined by URL parameter parser
    url = url_for('comment.comment', run_id=INVALID_RUN)

    resp = client.get(url)
    assert resp.status_code == 404

    content = resp.json
    assert 'data' not in content
