from flask import Blueprint

from informatics_front.view.course.workshop.invite import JoinWorkshopApi
from informatics_front.view.course.workshop.workshop import WorkshopApi

workshop_blueprint = Blueprint('workshop', __name__, url_prefix='/api/v1/workshop')

workshop_blueprint.add_url_rule('/<int:workshop_id>', methods=('POST',),
                                view_func=JoinWorkshopApi.as_view('join'))

workshop_blueprint.add_url_rule('/<int:workshop_id>', methods=('GET',),
                                view_func=WorkshopApi.as_view('read'))
