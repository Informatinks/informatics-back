from flask.views import MethodView
from werkzeug.exceptions import NotFound, BadRequest

from informatics_front import current_user
from informatics_front.model import db
from informatics_front.model.workshop.workshop import WorkShop, WorkshopStatus
from informatics_front.model.workshop.workshop_connection import WorkshopConnection
from informatics_front.utils.auth import login_required
from informatics_front.utils.response import jsonify


class JoinWorkshopApi(MethodView):
    @login_required
    def post(self, workshop_id: int):
        workshop = db.session.query(WorkShop).get(workshop_id)
        self._reject_if_wrong_permissions(workshop)

        user_id = current_user.id
        workshop_connection = db.session.query(WorkshopConnection)\
            .filter(WorkshopConnection.user_id == user_id) \
            .filter(WorkshopConnection.workshop_id == workshop_id) \
            .one_or_none()

        if workshop_connection is not None:
            raise BadRequest('You are already in this workshop')

        workshop_connection = WorkshopConnection(user_id=user_id, workshop_id=workshop_id)
        db.session.add(workshop_connection)
        db.session.commit()
        # TODO: return connection object
        return jsonify({})

    @classmethod
    def _reject_if_wrong_permissions(cls, workshop: WorkShop):
        if workshop.status != WorkshopStatus.ONGOING:
            raise NotFound(f'Workshop with id #{workshop.id} is not found')

