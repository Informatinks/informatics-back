import io
import pytest

from unittest.mock import Mock
from werkzeug.datastructures import FileStorage

from informatics_front.utils.services.internal_rmatics import InternalRmatics

PROBLEM_ID = 1
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
    client.get_runs_filter(PROBLEM_ID, {'a': 1}, is_admin=True)
    client.client.get_data.assert_called_with(
        f'{client.service_url}/problem/{PROBLEM_ID}/submissions/',
        params={'a': 1, 'is_admin': True},
        default=[],
        silent=True
    )


@pytest.mark.internal_rmatics
def test_send_submit(client):
    data = {'lang_id': 1, 'user_id': 2, 'statement_id': 3}
    file = FileStorage(
        io.BytesIO(b'sample data'), filename='test.cpp', content_type='application/pdf'
    )

    client.send_submit(
        file, data['user_id'], PROBLEM_ID, data['statement_id'], data['lang_id']
    )
    client.client.post_data.assert_called_with(
        f'{client.service_url}/problem/trusted/{PROBLEM_ID}/submit_v2',
        json=data,
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
    problems = [1, 2, 3]
    users = [4, 5, 6]
    client.get_monitor(problems, users, None)
    client.client.get_data.assert_called_with(
        f'{client.service_url}/monitor/problem_monitor',
        params={'user_id': users,
                'problem_id': problems},
        silent=True,
        default=[]
    )


@pytest.mark.internal_rmatics
def test_get_monitor_with_time_before(client):
    problems = [1, 2, 3]
    users = [4, 5, 6]
    time_before = 123456789
    client.get_monitor(problems, users, time_before)
    client.client.get_data.assert_called_with(
        f'{client.service_url}/monitor/problem_monitor',
        params={'user_id': users,
                'problem_id': problems,
                'time_before': time_before},
        silent=True,
        default=[]
    )

