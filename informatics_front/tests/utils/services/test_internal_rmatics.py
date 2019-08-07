import io
from unittest.mock import Mock

import pytest
from werkzeug.datastructures import FileStorage

from informatics_front.utils.services.internal_rmatics import InternalRmatics

PROBLEM_ID = 1
CONTEST_ID = 2
LANG_ID = 1
RUN_ID = 2
USER_ID = 666
CLIENT_SERVICE_URL = 'foo'


@pytest.fixture
def client():
    client = InternalRmatics()
    client.service_url = CLIENT_SERVICE_URL
    client.client = Mock()
    return client


@pytest.mark.internal_rmatics
def test_get_runs_filter(client):
    client.get_runs_filter(PROBLEM_ID, CONTEST_ID, {'a': 1})
    client.client.get_data.assert_called_with(
        f'{client.service_url}/problem/{PROBLEM_ID}/submissions/',
        params={
            'a': 1,
            'context_source': InternalRmatics.default_context_source,
            'context_id': CONTEST_ID,
            'show_hidden': True,
        },
        default=[],
        silent=True
    )


@pytest.mark.internal_rmatics
def test_send_submit(client):
    expected_url = f'{CLIENT_SERVICE_URL}/problem/trusted/{PROBLEM_ID}/submit_v2'
    expected_call_args = {
        'lang_id': LANG_ID,
        'user_id': USER_ID,

        # Context params
        'context_id': CONTEST_ID,
        'context_source': InternalRmatics.default_context_source,
        'is_visible': False
    }
    file = FileStorage(
        io.BytesIO(b'sample data'), filename='test.cpp', content_type='application/pdf'
    )

    client.send_submit(file, USER_ID, PROBLEM_ID, CONTEST_ID, LANG_ID)
    client.client.post_data.assert_called_with(
        expected_url,
        json=expected_call_args,
        files={'file': file.stream},
        silent=True
    )


@pytest.mark.internal_rmatics
def test_get_run_source(client):
    client.get_run_source(RUN_ID, USER_ID, is_admin=True)
    client.client.get_data.assert_called_with(
        f'{client.service_url}/problem/run/{RUN_ID}/source/',
        params={'user_id': USER_ID, 'is_admin': True},
        silent=True
    )


@pytest.mark.internal_rmatics
def test_get_full_run_protocol(client):
    client.get_full_run_protocol(RUN_ID, USER_ID, is_admin=True)
    client.client.get_data.assert_called_with(
        f'{client.service_url}/problem/run/{RUN_ID}/protocol',
        params={'user_id': USER_ID, 'is_admin': True},
        silent=True
    )


@pytest.mark.internal_rmatics
def test_get_monitor(client):
    contest_id = 1
    problems = [1, 2, 3]
    users = [4, 5, 6]
    client.get_monitor(contest_id, problems, users, None)
    client.client.get_data.assert_called_with(
        f'{client.service_url}/monitor/problem_monitor',
        params={
            'user_id': users,
            'problem_id': problems,

            'context_id': contest_id,
            'context_source': InternalRmatics.default_context_source,
            'show_hidden': True,
        },
        silent=True,
        default=[]
    )


@pytest.mark.internal_rmatics
def test_get_monitor_with_time_before(client):
    contest_id = 1
    problems = [1, 2, 3]
    users = [4, 5, 6]
    time_before = 123456789
    client.get_monitor(contest_id, problems, users, time_before)
    client.client.get_data.assert_called_with(
        f'{client.service_url}/monitor/problem_monitor',
        params={
            'user_id': users,
            'problem_id': problems,
            'time_before': time_before,

            'context_id': contest_id,
            'context_source': InternalRmatics.default_context_source,
            'show_hidden': True,
        },
        silent=True,
        default=[]
    )
