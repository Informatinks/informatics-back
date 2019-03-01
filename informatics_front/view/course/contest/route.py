from flask import Blueprint

from informatics_front.view.course.contest.contest import ContestApi
from informatics_front.view.course.contest.problem import ProblemApi, ProblemSubmissionApi

contest_blueprint = Blueprint('contest', __name__, url_prefix='/api/v1/contest')


contest_blueprint.add_url_rule('/<int:course_module_id>', methods=('GET', ),
                               view_func=ContestApi.as_view('contest'))

contest_blueprint.add_url_rule('/problem/<int:problem_id>', methods=('GET', ),
                               view_func=ProblemApi.as_view('problem'))

contest_blueprint.add_url_rule('/problem/<int:problem_id>/submission', methods=('GET', 'POST'),
                               view_func=ProblemSubmissionApi.as_view('submissions'))
