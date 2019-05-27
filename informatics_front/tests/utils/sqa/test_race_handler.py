# from unittest import TestCase
import pytest

from informatics_front.model import db
from informatics_front.model.workshop.workshop import WorkShop
from informatics_front.utils.enums import WorkshopStatus
from informatics_front.utils.sqla.race_handler import get_or_create, _get_object, _create_object

WORKSHOP_NAME = 'foo'
WORKSHOP_ACCESS_TOKEN = 'bar'
ws_kwargs = {
    'name': WORKSHOP_NAME,
    'status': WorkshopStatus.ONGOING,
    'access_token': WORKSHOP_ACCESS_TOKEN
}


@pytest.mark.race_handler
def test_raw_create_uncommited_object(app, ):
    object_ = _create_object(WorkShop, **ws_kwargs)
    db.session.rollback()

    assert db.session.query(WorkShop).filter_by(**ws_kwargs).one_or_none() is None, 'object not should be created'


@pytest.mark.race_handler
def test_raw_create_commited_object(app, ):
    assert db.session.query(WorkShop).filter_by(
        **ws_kwargs).one_or_none() is None, 'object should not exist before test'

    try:
        object_ = _create_object(WorkShop, **ws_kwargs)
        db.session.commit()
        db.session.rollback()

        assert db.session.query(WorkShop).filter_by(**ws_kwargs).one_or_none() is not None, 'object should be created'
    finally:
        # unconditioned object deletion
        db.session.delete(object_)
        db.session.commit()


@pytest.mark.race_handler
def test_get_object(app, ):
    assert db.session.query(WorkShop).filter_by(
        **ws_kwargs).one_or_none() is None, 'object should not exist before test'

    ws: WorkShop = WorkShop(**ws_kwargs)
    db.session.add(ws)
    db.session.commit()

    try:
        found_object = _get_object(WorkShop, **ws_kwargs)
        assert ws.id is found_object.id, 'proper object should be found'
    finally:
        # unconditioned object deletion
        db.session.delete(ws)
        db.session.commit()


@pytest.mark.race_handler
def test_get_or_create_create_uncommit(app, ):
    assert db.session.query(WorkShop).filter_by(
        **ws_kwargs).one_or_none() is None, 'object should not exist before test'

    object_1, is_created = get_or_create(WorkShop, **ws_kwargs)
    assert is_created is True

    db.session.rollback()

    assert db.session.query(WorkShop).count() == 0, 'object should not be created'


@pytest.mark.race_handler
def test_get_or_create_create_commit(app, ):
    assert db.session.query(WorkShop).filter_by(
        **ws_kwargs).one_or_none() is None, 'object should not exist before test'

    try:
        object_1, is_created = get_or_create(WorkShop, **ws_kwargs)
        assert is_created is True
        db.session.commit()

        db.session.rollback()

        assert db.session.query(WorkShop).count() == 1, 'object should exist after session rollback'
    finally:
        # unconditioned object deletion
        db.session.delete(object_1)
        db.session.commit()


@pytest.mark.race_handler
def test_get_or_create_get(app, ):
    assert db.session.query(WorkShop).filter_by(
        **ws_kwargs).one_or_none() is None, 'object should not exist before test'

    ws: WorkShop = WorkShop(**ws_kwargs)
    db.session.add(ws)
    db.session.commit()

    try:
        object_1, is_created = get_or_create(WorkShop, **ws_kwargs)
        assert is_created is False

        assert object_1 is not None, 'object should be got'
    finally:
        # unconditioned object deletion
        db.session.delete(object_1)
        db.session.commit()
