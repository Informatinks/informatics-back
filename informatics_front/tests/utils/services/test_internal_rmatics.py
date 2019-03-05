import io
import pytest

from unittest.mock import Mock
from werkzeug.datastructures import FileStorage

from informatics_front.utils.services.internal_rmatics import InternalRmatics

PROBLEM_ID = 1
CLIENT_SERVICE_URL = 'foo'


@pytest.mark.internal_rmatics
def test_get_runs_filter():
    client = InternalRmatics()
    client.service_url = CLIENT_SERVICE_URL
    client.client = Mock()

    client.get_runs_filter(PROBLEM_ID, {'a': 1}, is_admin=True)
    client.client.get_data.assert_called_with(
        f'{client.service_url}/problem/{PROBLEM_ID}/submissions/',
        params={'a': 1, 'is_admin': True},
        default=[],
        silent=True
    )


@pytest.mark.internal_rmatics
def test_send_submit():
    client = InternalRmatics()
    client.service_url = CLIENT_SERVICE_URL
    client.client = Mock()

    data = {
        'lang_id': 1,
        'user_id': 2,
        'statement_id': 3
    }
    file = FileStorage(io.BytesIO(b'sample data'), filename='test.cpp', content_type='application/pdf')

    client.send_submit(file, data['user_id'], PROBLEM_ID, data['statement_id'], data['lang_id'])
    client.client.post_data.assert_called_with(
        f'{client.service_url}/problem/trusted/{PROBLEM_ID}/submit_v2',
        json=data,
        files={'file': file.stream},
        silent=True
    )
