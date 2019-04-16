import datetime

from informatics_front.model.contest.contest_instance import ContestInstance
from informatics_front.model.workshop.contest_connection import ContestConnection


def test_is_available_by_duration():
    current_time = datetime.datetime.utcnow()
    available_contest = ContestInstance(time_start=current_time - datetime.timedelta(seconds=1),
                                        time_stop=current_time + datetime.timedelta(days=2))
    assert available_contest.is_available_by_duration()

    not_started_contest = ContestInstance(time_start=current_time + datetime.timedelta(days=1),
                                          time_stop=current_time + datetime.timedelta(days=2))
    assert not not_started_contest.is_available_by_duration()

    finished_contest = ContestInstance(time_start=current_time - datetime.timedelta(days=2),
                                       time_stop=current_time - datetime.timedelta(days=1))

    assert not finished_contest.is_available_by_duration()


def test_is_available_for_connection():
    contest = ContestInstance(is_virtual=True,
                              virtual_duration=datetime.timedelta(hours=1))

    current_time = datetime.datetime.utcnow()
    allowed_cc = ContestConnection(created_at=current_time)

    assert contest.is_available_for_connection(allowed_cc)

    finished_cc = ContestConnection(created_at=current_time - datetime.timedelta(hours=2))

    assert not contest.is_available_for_connection(finished_cc)
