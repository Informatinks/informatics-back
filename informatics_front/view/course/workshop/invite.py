from flask import request
from flask.views import MethodView
from marshmallow import fields
from webargs.flaskparser import parser
from werkzeug.exceptions import NotFound

from informatics_front.model import db
from informatics_front.model.workshop.workshop import WorkShop, WorkshopStatus
from informatics_front.model.workshop.workshop_connection import WorkshopConnection
from informatics_front.utils.auth.middleware import login_required
from informatics_front.utils.auth.request_user import current_user
from informatics_front.utils.response import jsonify
from informatics_front.utils.sqla.race_handler import get_or_create
from informatics_front.view.course.workshop.serializers.workshop_connection import WorkshopConnectionSchema


class JoinWorkshopApi(MethodView):
    post_args = {
        'token': fields.String(),
    }

    @login_required
    def post(self, workshop_id: int):
        args = parser.parse(self.post_args, request)

        workshop = db.session.query(WorkShop) \
            .filter_by(id=workshop_id,
                       status=WorkshopStatus.ONGOING,
                       access_token=args.get('token')) \
            .one_or_none()

        if workshop is None:
            raise NotFound(f'Workshop is not found')

        wc, is_created = get_or_create(WorkshopConnection, user_id=current_user.id, workshop_id=workshop_id)

        if is_created is True:
            db.session.commit()

        wc_schema = WorkshopConnectionSchema()
        response = wc_schema.dump(wc)

        return jsonify(response.data)
