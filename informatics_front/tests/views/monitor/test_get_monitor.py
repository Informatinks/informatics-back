import datetime
from unittest.mock import patch, MagicMock

from flask import url_for

from informatics_front.model import db
from informatics_front.model.contest.contest import Contest
from informatics_front.model.contest.monitor import WorkshopMonitor
from informatics_front.utils.enums import WorkshopMonitorUserVisibility
from informatics_front.model.user.user import SimpleUser
from informatics_front.view.course.monitor.monitor import WorkshopMonitorApi


def test_get_users(applied_workshop_connection):
    workshop = applied_workshop_connection.workshop

    users = WorkshopMonitorApi._find_users_on_workshop(workshop.id)

    assert users == [applied_workshop_connection.user]


def test_get_users_when_for_user_only(authorized_user):
    monitor = WorkshopMonitor(user_visibility=WorkshopMonitorUserVisibility.FOR_USER_ONLY)

    with patch('informatics_front'
               '.view.course'
               '.monitor.monitor'
               '.WorkshopMonitorApi._find_users_on_workshop') as mock_find_users:
        users = WorkshopMonitorApi._get_users(monitor, 123)
    mock_find_users.assert_not_called()
    assert users[0].id == authorized_user.user.id


def test_get_users_when_public(authorized_user):
    monitor = WorkshopMonitor(user_visibility=WorkshopMonitorUserVisibility.FULL)

    with patch('informatics_front'
               '.view.course'
               '.monitor.monitor'
               '.WorkshopMonitorApi._find_users_on_workshop') as mock_find_users:
        mock_find_users.return_value = ['imuser']
        users = WorkshopMonitorApi._get_users(monitor, None)
    mock_find_users.assert_called_once()
    assert users == ['imuser']


def test_get_users_by_group(authorized_user, users, group):
    user_ids = [user['id'] for user in users]
    expected_users = db.session.query(SimpleUser).filter(SimpleUser.id.in_(user_ids)).all()

    monitor = WorkshopMonitor(user_visibility=WorkshopMonitorUserVisibility.FULL)

    users = WorkshopMonitorApi._get_users(monitor, group.id)

    assert users == expected_users


def test_ensure_permissions_without_conn(applied_workshop_connection):
    workshop = applied_workshop_connection.workshop
    assert not WorkshopMonitorApi._ensure_permissions(workshop.id)


def test_ensure_permissions(accepted_workshop_connection):
    workshop = accepted_workshop_connection.workshop
    assert WorkshopMonitorApi._ensure_permissions(workshop.id)


def test_get_raw_data_by_contest(ongoing_workshop):
    time_freeze = MagicMock()
    time_freeze.utctimestamp.return_value = '123'
    monitor = WorkshopMonitor(freeze_time=time_freeze)
    runs = [{'my': 'data'}]
    user_ids = [1, 2, 3]
    contest = ongoing_workshop['contest']

    with patch('informatics_front'
               '.view.course'
               '.monitor.monitor'
               '.internal_rmatics.get_monitor') as mock_get_monitor:
        mock_get_monitor.return_value = runs, 200
        response = WorkshopMonitorApi._get_raw_data_by_contest(monitor, user_ids, contest)

    assert response == runs

    problems = contest.statement.problems
    problem_ids = list(p.id for p in problems)

    mock_get_monitor.assert_called_with(problem_ids, user_ids, time_freeze.utctimestamp.return_value)


def test_make_function_user_start_time_when_not_virtual():
    time_start = '123'
    c = Contest(is_virtual=False, time_start=time_start)
    func = WorkshopMonitorApi._make_function_getting_user_start_time(c, [1, 2, 3])
    assert func() == time_start


def test_make_function_user_start_time_when_virtual(contest_connection):
    c = contest_connection.contest
    c.is_virtual = True
    func = WorkshopMonitorApi._make_function_getting_user_start_time(c, [1, 2, contest_connection.user_id])

    assert func(contest_connection.user_id) == contest_connection.created_at.astimezone()
    assert func(123) == datetime.datetime.utcfromtimestamp(0).astimezone()


def test_simple_view(client, monitor, accepted_workshop_connection):
    workshop = accepted_workshop_connection.workshop
    url = url_for('monitor.workshop', workshop_id=workshop.id)
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_with_group(client, monitor, accepted_workshop_connection, group):
    workshop = accepted_workshop_connection.workshop
    url = url_for('monitor.workshop', workshop_id=workshop.id, group_id=group.id)
    resp = client.get(url)
    assert resp.status_code == 200