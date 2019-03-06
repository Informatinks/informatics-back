from unittest.mock import patch

import pytest
from flask import url_for, g


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
                        'big_corr':1 , 'output': 1, 'big_output': 1,
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
