import pytest
from flask import url_for, g
from unittest.mock import patch

from informatics_front.model.contest.contest import ContestProtocolVisibility
from informatics_front.view.course.contest.run import RunProtocolApi

NON_EXISTING_USER = -1
NON_EXISTING_RUN = 1337
INVALID_RUN = -1


@pytest.mark.run
def test_get_run_source(client, authorized_user):
    with patch('informatics_front.plugins.internal_rmatics.get_run_source') as get_run_source:
        get_run_source.return_value = ({}, 200)
        run_id = 3
        url = url_for('run.source', run_id=run_id)
        resp = client.get(url)

        assert resp.status_code == 200

        get_run_source.assert_called_with(run_id, g.user['id'])


@pytest.mark.comment
@pytest.mark.usefixtures('authorized_user')
def test_get_run_comments(client, users, comments):
    """Ensure for every run for current authorized user
       we've got exactly one particular comment"""
    for comment in comments:
        py_run_id = comment.py_run_id
        url = url_for('run.comments', run_id=py_run_id)

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
    url = url_for('run.comments', run_id=comment.py_run_id)

    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert len(content) == 0


@pytest.mark.comment
def test_get_run_comments_for_invalid_run_id(client, authorized_user):
    """Ensure invalid run_id returns 0 comments"""
    url = url_for('run.comments', run_id=NON_EXISTING_RUN)

    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert len(content) == 0

    # for non-integer run should return 404, defined by URL parameter parser
    url = url_for('run.comments', run_id=INVALID_RUN)

    resp = client.get(url)
    assert resp.status_code == 404

    content = resp.json
    assert 'data' not in content


class TestGetRunProtocol:
    def test_remove_fields_from_full_protocol(self):
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

        resp = RunProtocolApi._remove_fields_from_full_protocol(full_protocol)

        assert resp == {'tests': {'data': {}}}, 'All of fields were filtered'

    def test_remove_all_after_bad_test(self):
        protocol = {'tests':
                        {
                            '1': {'status': 'OK'},
                            '2': {'status': 'OK'},
                            '3': {'status': 'NOT OK'},
                            '4': {'status': 'OK'},
                            '5': {'status': 'NOT OK'},
                        }
                    }
        res = RunProtocolApi._remove_all_after_bad_test(protocol)

        assert res.get('tests') == {'1': {'status': 'OK'},
                                    '2': {'status': 'OK'},
                                    '3': {'status': 'NOT OK'}}, \
            'should stay only last failed test'

    @pytest.mark.run
    def test_get_run_protocol(self, statement, contest_builder, client, authorized_user):
        contest = contest_builder(protocol_visibility=ContestProtocolVisibility.FIRST_BAD_TEST)
        full_protocol = {
            'audit': [],
            'tests': {
                '1': {
                    'status': 'OK',
                    'input': 1, 'big_input': 1, 'corr': 1,
                    'big_corr': 1, 'output': 1, 'big_output': 1,
                    'checker_output': 1, 'error_output': 1, 'extra': 1
                },
                '2': {
                    'status': 'OK'
                },
                '3': {
                    'status': 'WA'
                },
                '4': {
                    'status': 'OK'
                },
            }
        }
        run_id = 3
        url = url_for('contest.run_protocol',
                      contest_id=contest.id,
                      problem_id=statement.problems[0].id,
                      run_id=run_id)

        with patch('informatics_front.plugins.internal_rmatics.get_full_run_protocol',
                   return_value=(full_protocol, 200,)) \
                as get_full_run_protocol:

            resp = client.get(url)

        assert resp.status_code == 200

        get_full_run_protocol.assert_called_with(run_id, g.user['id'])

        assert resp.json['data'] == {'tests':
                                         {
                                             '1': {'status': 'OK'},
                                             '2': {'status': 'OK'},
                                             '3': {'status': 'WA'}
                                         }
                                     }, \
            'All of fields were filtered'
