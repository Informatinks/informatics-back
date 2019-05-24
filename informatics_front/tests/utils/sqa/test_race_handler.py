# from unittest import TestCase
import pytest

from informatics_front.model import db
from informatics_front.model.workshop.workshop import WorkShop
from informatics_front.utils.enums import WorkshopStatus
from informatics_front.utils.sqla.race_handler import RaceHandler

WORKSHOP_NAME = 'foo'
WORKSHOP_ACCESS_TOKEN = 'bar'
ws_kwargs = {
    'name': WORKSHOP_NAME,
    'status': WorkshopStatus.ONGOING,
    'access_token': WORKSHOP_ACCESS_TOKEN
}


@pytest.mark.race_handler
def test_create_object(app, ):
    assert db.session.query(WorkShop).filter_by(**ws_kwargs).one_or_none() is None, 'object should not exist'

    try:
        object_ = RaceHandler._create_object(WorkShop, **ws_kwargs)

        assert db.session.query(WorkShop).filter_by(
            **ws_kwargs).one_or_none() is not None, 'object should be created'

        db.session.refresh(object_)
        assert object_.id is not None, 'created object should have id'

        for k in ws_kwargs:
            assert getattr(object_, k) == ws_kwargs.get(k), 'created object should have correct passed atributes'
    finally:
        # unconditioned object deletion
        db.session.delete(object_)
        db.session.commit()


@pytest.mark.race_handler
def test_get_object(app, ):
    assert db.session.query(WorkShop).filter_by(**ws_kwargs).one_or_none() is None, 'object should not exist'

    try:
        created_object = RaceHandler._create_object(WorkShop, **ws_kwargs)
        found_object = RaceHandler._get_object(WorkShop, **ws_kwargs)

        assert created_object.id is found_object.id, 'proper object should be found'
    finally:
        # unconditioned object deletion
        db.session.delete(created_object)
        db.session.commit()


@pytest.mark.race_handler
def test_get_or_create(app, ):
    assert db.session.query(WorkShop).count() == 0, 'no object should exist'

    try:
        object_1 = RaceHandler.get_or_create(WorkShop, **ws_kwargs)
        assert db.session.query(WorkShop).count() == 1, 'object should be created'

        object_2 = RaceHandler.get_or_create(WorkShop, **ws_kwargs)
        assert db.session.query(WorkShop).count() == 1, 'no new objects should be created'

        assert object_1.id == object_2.id, 'returned object is the same as created'
    finally:
        # unconditioned object deletion
        db.session.delete(object_1)
        db.session.commit()


@pytest.mark.race_handler
def test_auto_rollback_transaction(app, ):
    assert db.session.query(WorkShop).count() == 0, 'no object should exist'

    try:
        object_ = RaceHandler.get_or_create(WorkShop, **ws_kwargs)

        db.session.rollback()
        assert db.session.query(
            WorkShop).count() == 1, 'global auto-rollback session should not destroy created objects'
    finally:
        # unconditioned object deletion
        db.session.delete(object_)
        db.session.commit()
