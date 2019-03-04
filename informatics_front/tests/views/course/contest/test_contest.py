import pytest

from flask import url_for

NON_EXISTING_ID = -1


@pytest.mark.contest_problem
def test_contest(client, authorized_user, course_module, problem):
    contest = course_module.instance

    url = url_for('contest.contest', course_module_id=NON_EXISTING_ID)
    resp = client.get(url)
    assert resp.status_code == 404

    url = url_for('contest.contest', course_module_id=course_module.id)
    resp = client.get(url)
    assert resp.status_code == 200

    content = resp.json
    assert 'data' in content

    content = content['data']
    assert content.get('id') == course_module.id

    for field in ('name', 'summary', ):
        assert getattr(contest, field) == content.get(field, -1)  # avoid None is None comparison

    assert len(content['problems']) == 1

    problem_content = content['problems'][0]

    for field in ('id', 'name'):
        assert getattr(problem, field) == problem_content.get(field, -1)  # avoid None is None comparison

    assert problem_content['rank'] == 1
