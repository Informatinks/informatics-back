from typing import Optional

from sqlalchemy.exc import IntegrityError

from informatics_front.model import db


def get_or_create(model_class: db.Model, **kwargs) -> db.Model:
    """Safe create objects, which may exist only as one instance

    Avoids race conditions or Integrity errors on duplicated inserts.

    :param model_class: SQLAchemy model for instance to be found or created
    :param kwargs: model instance attributes, with which it should be creted
    :return: exisitng model instance, which was created or found in DB
    """
    return _get_object(model_class, **kwargs) or \
           _create_object(model_class, **kwargs)


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


def _create_object(model_class: db.Model, **kwargs) -> db.Model:
    """

    :param model: SQLAchemy model to create instance of
    :param kwargs: model instance attributes for insertion
    :return: created model instance
    """
    cc = model_class(**kwargs)
    db.session.begin_nested()
    try:
        db.session.add(cc)
        db.session.commit()
        # HACK: prevent auto rollback transction
        # to flush created object
        db.session.commit()
        db.session.refresh(cc)
    except IntegrityError:
        db.session.rollback()
        cc = _get_object(model_class, **kwargs)
    return cc
