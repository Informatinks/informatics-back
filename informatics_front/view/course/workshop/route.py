from flask import Blueprint

from informatics_front.view.course.workshop.invite import JoinWorkshopApi

workshop_blueprint = Blueprint('workshop', __name__, url_prefix='/api/v1/workshop')

workshop_blueprint.add_url_rule('/<int:workshop_id>', methods=('POST',),
                                view_func=JoinWorkshopApi.as_view('join'))


