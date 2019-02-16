from flask import Blueprint

from informatics_front.view.course.contest.contest import ContestApi
from informatics_front.view.course.contest.problem import ProblemApi

contest_blueprint = Blueprint('contest', __name__, url_prefix='/contest')


contest_blueprint.add_url_rule('/<int:course_module_id>', methods=('GET', ),
                               view_func=ContestApi.as_view('contest'))

contest_blueprint.add_url_rule('/problem/<int:problem_id>', methods=('GET', ),
                               view_func=ProblemApi.as_view('problem'))
