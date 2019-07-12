import datetime

from informatics_front.model.contest.contest import Contest
from informatics_front.model.workshop.contest_connection import ContestConnection


def test_is_available_by_duration():
    current_time = datetime.datetime.utcnow()
    available_contest = Contest(time_start=current_time - datetime.timedelta(seconds=1),
                                time_stop=current_time + datetime.timedelta(days=2))
    assert available_contest._is_available_by_duration()

    not_started_contest = Contest(time_start=current_time + datetime.timedelta(days=1),
                                  time_stop=current_time + datetime.timedelta(days=2))
    assert not not_started_contest._is_available_by_duration()

    finished_contest = Contest(time_start=current_time - datetime.timedelta(days=2),
                               time_stop=current_time - datetime.timedelta(days=1))

    assert not finished_contest._is_available_by_duration()


def test_is_available_for_connection():
    contest = Contest(is_virtual=True,
                      virtual_duration=datetime.timedelta(hours=1))

    current_time = datetime.datetime.utcnow()
    allowed_cc = ContestConnection(created_at=current_time)

    assert contest._is_available_for_connection(allowed_cc)

    finished_cc = ContestConnection(created_at=current_time - datetime.timedelta(hours=2))

    assert not contest._is_available_for_connection(finished_cc)


def test_is_not_started_virtual():
    virtual_contest = Contest(is_virtual=True)

    cc = ContestConnection()
    assert not virtual_contest.is_not_started(cc)
    assert virtual_contest.is_not_started(None)


def test_is_not_started_not_virtual():
    current_time = datetime.datetime.utcnow()

    available_contest = Contest(time_start=current_time - datetime.timedelta(hours=1),
                                is_virtual=False)
    assert not available_contest.is_not_started(None)

    not_available_contest = Contest(time_start=current_time + datetime.timedelta(hours=1),
                                    is_virtual=False)
    assert not_available_contest.is_not_started(None)
