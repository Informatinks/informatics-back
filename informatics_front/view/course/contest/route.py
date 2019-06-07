from flask import Blueprint

from informatics_front.view.course.contest.contest import ContestApi
from informatics_front.view.course.contest.problem import ProblemApi, ProblemSubmissionApi
from informatics_front.view.course.contest.run import RunSourceApi, RunProtocolApi, RunCommentsApi

contest_blueprint = Blueprint('contest', __name__, url_prefix='/api/v1/contest/<int:contest_id>')

contest_blueprint.add_url_rule('/', methods=('GET',),
                               view_func=ContestApi.as_view('contest'))

contest_blueprint.add_url_rule('/problem/<int:problem_id>', methods=('GET',),
                               view_func=ProblemApi.as_view('problem'))

contest_blueprint.add_url_rule('/problem/<int:problem_id>/submission', methods=('GET', 'POST'),
                               view_func=ProblemSubmissionApi.as_view('submissions'))

contest_blueprint.add_url_rule('/problem/<int:problem_id>/run/<int:run_id>/protocol', methods=('GET',),
                               view_func=RunProtocolApi.as_view('run_protocol'))


run_blueprint = Blueprint('run', __name__, url_prefix='/api/v1/run/<int:run_id>')

run_blueprint.add_url_rule('/source', methods=('GET',),
                           view_func=RunSourceApi.as_view('source'))

run_blueprint.add_url_rule('/comments', methods=('GET',),
                           view_func=RunCommentsApi.as_view('comments'))
