from flask.views import MethodView
from marshmallow import MarshalResult
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import NotFound

from informatics_front.utils.auth.request_user import current_user
from informatics_front.model import db
from informatics_front.model.contest.contest import Contest
from informatics_front.model.workshop.workshop import WorkShop, WorkshopStatus
from informatics_front.model.workshop.workshop_connection import WorkshopConnection, WorkshopConnectionStatus
from informatics_front.utils.auth.middleware import login_required
from informatics_front.utils.response import jsonify
from informatics_front.view.course.workshop.serializers.workshop import WorkshopSchema


class WorkshopApi(MethodView):
    @login_required
    def get(self, workshop_id):
        # Get first as only one WorkshopConnection may exist due to unique constraints
        workshop_connection: WorkshopConnection = db.session.query(WorkshopConnection) \
            .filter(WorkshopConnection.workshop_id == workshop_id,
                    WorkshopConnection.user_id == current_user.id,
                    # only accepted connections can be seen or participated at by students
                    WorkshopConnection.status == WorkshopConnectionStatus.ACCEPTED,
                    # Workshop should be active and visible
                    WorkShop.status == WorkshopStatus.ONGOING) \
            .options(joinedload(WorkshopConnection.workshop)
                     .joinedload(WorkShop.contests)
                     .joinedload(Contest.statement)) \
            .one_or_none()

        if workshop_connection is None:
            raise NotFound(f'Cannot find workshop id #{workshop_id}')

        workshop_serializer: WorkshopSchema = WorkshopSchema(exclude=[
            'contests.statement.problems',
        ])
        response: MarshalResult = workshop_serializer.dump(workshop_connection.workshop)

        return jsonify(response.data)
