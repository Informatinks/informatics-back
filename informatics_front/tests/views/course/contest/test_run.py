from unittest.mock import patch

import pytest
from flask import url_for, g

NON_EXISTING_USER = -1
NON_EXISTING_RUN = 1337
INVALID_RUN = -1


@pytest.mark.run
def test_get_run_source(client, authorized_user):
    with patch('informatics_front.internal_rmatics.get_run_source') as get_run_source:
        get_run_source.return_value = ({}, 200)
        run_id = 3
        url = url_for('contest.run_source', run_id=run_id)
        resp = client.get(url)

        assert resp.status_code == 200

        get_run_source.assert_called_with(run_id, g.user['id'])


@pytest.mark.run
def test_get_run_protocol(client, authorized_user):
    with patch('informatics_front.internal_rmatics.get_full_run_protocol') \
            as get_full_run_protocol:
        run_id = 3
        full_protocol = {
            'audit': [],
            'tests': {
                'data': {
                    'input': 1, 'big_input': 1, 'corr': 1,
                    'big_corr': 1, 'output': 1, 'big_output': 1,
                    'checker_output': 1, 'error_output': 1, 'extra': 1
                }
            }
        }

        get_full_run_protocol.return_value = (full_protocol, 200,)

        url = url_for('contest.run_protocol', run_id=run_id)
        resp = client.get(url)

        assert resp.status_code == 200

        get_full_run_protocol.assert_called_with(run_id, g.user['id'])

        assert resp.json['data'] == {'tests': {'data': {}}}, 'All of fields were filtered'


@pytest.mark.comment
def test_get_run_comments(client, users, authorized_user, comments):
    """Ensure for every run for current authorized user
       we've got exactly one particular comment"""
    for comment in comments:
        py_run_id = comment.py_run_id
        url = url_for('contest.run_comments', run_id=py_run_id)

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
def test_get_run_comments_for_invalid_user(client, authorized_user, comment):
    """Ensure invalid user in context returns 0 comments"""
    g.user['id'] = NON_EXISTING_USER
    url = url_for('contest.run_comments', run_id=comment.py_run_id)

    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert len(content) == 0


@pytest.mark.comment
def test_get_run_comments_for_invalid_run_id(client, authorized_user):
    """Ensure invalid run_id returns 0 comments"""
    url = url_for('contest.run_comments', run_id=NON_EXISTING_RUN)

    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert len(content) == 0

    # for non-integer run should return 404, defined by URL parameter parser
    url = url_for('contest.run_comments', run_id=INVALID_RUN)

    resp = client.get(url)
    assert resp.status_code == 404

    content = resp.json
    assert 'data' not in content
