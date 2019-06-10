from typing import Optional, Tuple

from sqlalchemy.exc import IntegrityError

from informatics_front.model import db


def get_or_create(model_class: db.Model, **kwargs) -> Tuple[db.Model, bool]:
    """Safe create objects, which may exist only as one instance

    Avoids race conditions or Integrity errors on duplicated inserts.

    :param model_class: SQLAchemy model for instance to be found or created
    :param kwargs: model instance attributes, with which it should be creted
    :return: Tuple of two elements:
        1. exisitng model instance. Wither created wor found in DB;
        2. boolean. True, if objects was created, otherwise False.
    """
    is_created = False
    object_ = _get_object(model_class, **kwargs)

    if object_ is None:
        object_, is_created = _create_object(model_class, **kwargs)

    return object_, is_created


def _get_object(model_class: db.Model, **kwargs) -> Optional[db.Model]:
    """Try to get instance of object to be created.

    May return None, if not found. We can use Optional[X] as a shorthand for Union[X, None].

    :param model: SQLAchemy model to find instance of
    :param kwargs: model instance attributes for query
    :return: found model instance or None, if not exist in db
    """
    return db.session.query(model_class) \
        .filter_by(**kwargs) \
        .one_or_none()


def _create_object(model_class: db.Model, **kwargs) -> Tuple[db.Model, bool]:
    """

    :param model: SQLAchemy model to create instance of
    :param kwargs: model instance attributes for insertion
    :return: created model instance
    """
    is_created = False
    object_ = model_class(**kwargs)

    db.session.begin_nested()
    try:
        db.session.add(object_)
        db.session.commit()
        db.session.refresh(object_)
        is_created = True
    except IntegrityError:
        db.session.rollback()
        object_ = _get_object(model_class, **kwargs)

    return object_, is_created
