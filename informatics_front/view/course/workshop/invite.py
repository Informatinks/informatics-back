from flask import request
from flask.views import MethodView
from marshmallow import fields
from webargs.flaskparser import parser
from werkzeug.exceptions import NotFound, BadRequest

from informatics_front.model import db
from informatics_front.model.workshop.workshop import WorkShop, WorkshopStatus
from informatics_front.model.workshop.workshop_connection import WorkshopConnection
from informatics_front.utils.auth.middleware import login_required
from informatics_front.utils.auth.request_user import current_user
from informatics_front.utils.response import jsonify


class JoinWorkshopApi(MethodView):
    get_args = {
        'token': fields.String(),
    }

    @login_required
    def get(self, workshop_id: int):
        # Will raise Error is not token supplied
        args = parser.parse(self.get_args, request)
        workshop = db.session.query(WorkShop).get(workshop_id)

        # Check access permissions
        self._reject_if_not_found(workshop)
        self._reject_if_wrong_permissions(workshop)
        self._reject_if_invalid_access_token(workshop, args.get('token'))

        user_id = current_user.id
        workshop_connection = db.session.query(WorkshopConnection) \
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
    def _reject_if_not_found(cls, workshop: WorkShop):
        if workshop is None:
            raise NotFound(f'Workshop with id #{workshop.id} is not found')

    @classmethod
    def _reject_if_invalid_access_token(cls, workshop: WorkShop, token):
        if workshop.access_token != token:
            raise BadRequest(f'Access token is not valid for this workshop')

    @classmethod
    def _reject_if_wrong_permissions(cls, workshop: WorkShop):
        if workshop.status != WorkshopStatus.ONGOING:
            raise NotFound(f'Workshop with id #{workshop.id} is not found')
