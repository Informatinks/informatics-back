import pytest

from informatics_front.model import db
from informatics_front.model.contest.monitor import WorkshopMonitor


@pytest.yield_fixture
def monitor(ongoing_workshop):
    m = WorkshopMonitor(workshop_id=ongoing_workshop['workshop'].id)
    db.session.add(m)
    db.session.commit()

    yield m

    db.session.delete(m)
