import pytest

from informatics_front.model import db
from informatics_front.model.workshop.workshop import WorkShop, WorkshopStatus

WORKSHOP_ACCESS_TOKEN = 'foo'


@pytest.yield_fixture
def empty_workshop():
    w = WorkShop(status=WorkshopStatus.ONGOING, access_token=WORKSHOP_ACCESS_TOKEN)
    db.session.add(w)
    db.session.commit()
    db.session.refresh(w)

    yield w

    db.session.delete(w)
    db.session.commit()
