from flask import Blueprint

from informatics_front.view.course.monitor.monitor import WorkshopMonitorApi

monitor_blueprint = Blueprint('monitor', __name__, url_prefix='/api/v1/workshop/<int:workshop_id>/monitor')

monitor_blueprint.add_url_rule('/', methods=('GET', ),
                               view_func=WorkshopMonitorApi.as_view('workshop'))
