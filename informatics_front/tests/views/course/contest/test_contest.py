import pytest

from flask import url_for

NON_EXISTING_ID = -1


@pytest.mark.contest_problem
def test_contest(client, authorized_user, workshop):

    contest = workshop['contest_instance']

    url = url_for('contest.contest', contest_instance_id=NON_EXISTING_ID)
    resp = client.get(url)
    assert resp.status_code == 404

    url = url_for('contest.contest', contest_instance_id=contest.id)
    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    # assert content.get('id') == contest.id

    # for field in ('name', 'summary',):
    #     assert getattr(contest, field) == content.get(field, -1)  # avoid None is None comparison

    assert len(content['problems']) == 3

    problem_content = content['problems'][0]

    assert problem_content['rank'] == 1
    assert problem_content['name'].startswith('Problem')
