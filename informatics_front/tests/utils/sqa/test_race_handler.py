# from unittest import TestCase
from unittest.mock import Mock, patch

import pytest

from informatics_front.model import db
from informatics_front.model.workshop.contest_connection import ContestConnection
from informatics_front.utils.sqla.race_handler import get_or_create, _get_object, _create_object


@pytest.mark.race_handler
def test_raw_create_uncommited_object(authorized_user, ongoing_workshop):
    object_, is_created = _create_object(ContestConnection, user_id=authorized_user.user.id,
                                         contest_id=ongoing_workshop.get('contest').id)
    assert object_ is not None, 'should return created object'
    assert is_created is True, 'should mark object as create'

    db.session.rollback()
    assert db.session.query(ContestConnection).count() == 0, 'object should not exist after session rollback'


@pytest.mark.race_handler
def test_raw_create_commited_object(authorized_user, ongoing_workshop):
    try:
        object_, is_created = _create_object(ContestConnection, user_id=authorized_user.user.id,
                                             contest_id=ongoing_workshop.get('contest').id)
        assert object_ is not None, 'should return created object'
        assert is_created is True, 'should mark object as create'

        db.session.commit()
        db.session.rollback()

        found_object = db.session.query(ContestConnection) \
            .filter_by(user_id=authorized_user.user.id, contest_id=ongoing_workshop.get('contest').id) \
            .one_or_none()
        assert object_ is found_object, 'object should be preserved and properly retrieved'

    finally:
        # unconditioned object deletion
        db.session.delete(object_)
        db.session.commit()


@pytest.mark.race_handler
def test_raw_create_handles_race_condition(authorized_user, ongoing_workshop):
    """_create_object normally should not be called, if object was previously found.

    However, when race contidion occurs, previous call of `_get_object` may return None even if object exists.
    In this case _create_object will still be called and should raise IntegrityError and further session rollback.
    """
    with patch('informatics_front.utils.sqla.race_handler.db.session.rollback',
               wraps=db.session.rollback) as rollback:
        try:
            # pre-create object
            cc: ContestConnection = ContestConnection(user_id=authorized_user.user.id,
                                                      contest_id=ongoing_workshop.get('contest').id)
            db.session.add(cc)
            db.session.commit()

            object_, is_created = _create_object(ContestConnection, user_id=authorized_user.user.id,
                                                 contest_id=ongoing_workshop.get('contest').id)
            rollback.assert_called_once()
            assert cc is object_, '_get_object should return existing object'
        finally:
            # unconditioned object deletion
            db.session.delete(cc)
            db.session.commit()


@pytest.mark.race_handler
def test_get_object(authorized_user, ongoing_workshop):
    cc: ContestConnection = ContestConnection(user_id=authorized_user.user.id,
                                              contest_id=ongoing_workshop.get('contest').id)
    db.session.add(cc)
    db.session.commit()

    try:
        found_object = _get_object(ContestConnection, user_id=authorized_user.user.id,
                                   contest_id=ongoing_workshop.get('contest').id)
        assert cc.id is found_object.id, 'proper object should be found'
    finally:
        # unconditioned object deletion
        db.session.delete(cc)
        db.session.commit()


@pytest.mark.race_handler
def test_get_or_create_create_get(authorized_user, ongoing_workshop):
    with patch('informatics_front.utils.sqla.race_handler._create_object') as create_object, \
            patch('informatics_front.utils.sqla.race_handler._get_object') as get_object:
        get_or_create(ContestConnection, user_id=authorized_user.user.id,
                      contest_id=ongoing_workshop.get('contest').id)

        get_object.assert_called()
        create_object.assert_not_called()


@pytest.mark.race_handler
def test_get_or_create_create_commit(authorized_user, ongoing_workshop):
    with patch('informatics_front.utils.sqla.race_handler._create_object') as create_object, \
            patch('informatics_front.utils.sqla.race_handler._get_object') as get_object:
        get_object.return_value = None  # force object creation
        create_object.return_value = (Mock(), True)

        get_or_create(ContestConnection, user_id=authorized_user.user.id,
                      contest_id=ongoing_workshop.get('contest').id)

        create_object.assert_called()
        get_object.assert_called()
