import datetime
from unittest.mock import patch, MagicMock

from flask import url_for
from dateutil.tz import UTC

from informatics_front.model import db, Problem
from informatics_front.model.contest.contest import Contest
from informatics_front.model.contest.monitor import WorkshopMonitor
from informatics_front.utils.enums import WorkshopMonitorUserVisibility, WorkshopConnectionStatus
from informatics_front.model.user.user import SimpleUser
from informatics_front.view.course.monitor.monitor import WorkshopMonitorApi


def test_get_users(workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.APPLIED)
    workshop = workshop_connection.workshop
    load_only_fields = ('id',)

    users = WorkshopMonitorApi._find_users_on_workshop(workshop.id, load_only_fields)

    assert users == [workshop_connection.user]


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


def test_ensure_permissions_without_conn(workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.APPLIED)
    workshop = workshop_connection.workshop
    assert not WorkshopMonitorApi._ensure_permissions(workshop.id)


def test_ensure_permissions(workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.ACCEPTED)
    workshop = workshop_connection.workshop
    assert WorkshopMonitorApi._ensure_permissions(workshop.id)


def test_get_raw_data_by_contest(ongoing_workshop):
    time_freeze = MagicMock()
    time_freeze.timestamp.return_value = '123'
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

    mock_get_monitor.assert_called_with(problem_ids, user_ids, int(time_freeze.timestamp.return_value))


def test_filter_not_started_contests(authorized_user):
    contests = [Contest(), Contest(), Contest()]
    for c in contests:
        c.problems = []

    with patch('informatics_front.model.contest.contest.Contest.is_started') as started:
        started.return_value = False
        assert [] == WorkshopMonitorApi._filter_not_started_contests(contests)


def test_filter_not_started_contests_when_started(authorized_user):
    contests = [Contest(), Contest(), Contest()]
    for c in contests:
        c.problems = []

    with patch('informatics_front.model.contest.contest.Contest.is_started') as started:
        started.return_value = True
        assert contests == WorkshopMonitorApi._filter_not_started_contests(contests)


def test_make_function_user_start_time_when_not_virtual():
    time_start = datetime.datetime.utcnow().replace(tzinfo=UTC)
    c = Contest(is_virtual=False, time_start=time_start)
    func = WorkshopMonitorApi._make_start_time_retriever(c, [1, 2, 3])
    assert func() == time_start


def test_make_function_user_start_time_when_virtual(contest_connection):
    c = contest_connection.contest
    c.is_virtual = True
    func = WorkshopMonitorApi._make_start_time_retriever(c, [1, 2, contest_connection.user_id])

    assert func(contest_connection.user_id) == contest_connection.created_at.astimezone()
    assert func(123) == datetime.datetime.utcfromtimestamp(0).astimezone()


def test_simple_view(client, monitor, workshop_connection_builder):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.ACCEPTED)
    workshop = workshop_connection.workshop
    url = url_for('monitor.workshop', workshop_id=workshop.id)
    resp = client.get(url)
    assert resp.status_code == 200


def test_view_with_group(client, monitor, workshop_connection_builder, group):
    workshop_connection = workshop_connection_builder(WorkshopConnectionStatus.ACCEPTED)
    workshop = workshop_connection.workshop
    url = url_for('monitor.workshop', workshop_id=workshop.id, group_id=group.id)
    resp = client.get(url)
    assert resp.status_code == 200