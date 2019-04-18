import pytest

from informatics_front.model import db
from informatics_front.model.workshop.workshop import WorkShop, WorkshopStatus


@pytest.yield_fixture
def empty_workshop():
    w = WorkShop(status=WorkshopStatus.ONGOING)
    db.session.add(w)
    db.session.commit()
    db.session.refresh(w)

    yield w

    db.session.delete(w)
    db.session.commit()
