from flask.views import MethodView
from sqlalchemy.orm import Load
from werkzeug.exceptions import NotFound, BadRequest

from informatics_front.model import db, Problem, StatementProblem, Statement
from informatics_front.model import CourseModule
from informatics_front.utils.auth import login_required
from informatics_front.utils.response import jsonify
from informatics_front.view.course.contest.serializers.contest import ContestSchema


class ContestApi(MethodView):
    # @login_required
    def get(self, course_module_id):
        course_module = db.session.query(CourseModule) \
            .filter(CourseModule.id == course_module_id) \
            .filter(CourseModule.visible == 1) \
            .one_or_none()

        if course_module is None:
            raise NotFound(f'Cannot find course module id #{course_module_id}')

        contest = course_module.instance

        if not isinstance(contest, Statement):
            raise BadRequest('This resource is not implemented yet')

        problems_statement_problems = db.session.query(Problem, StatementProblem) \
            .join(StatementProblem, StatementProblem.problem_id == Problem.id) \
            .filter(StatementProblem.statement_id == contest.id) \
            .filter(Problem.hidden.isnot(True)) \
            .options(Load(Problem).load_only('id', 'name')) \
            .options(Load(StatementProblem).load_only('rank'))

        problems = []
        # Yes it is ugly but I think its better than rewrite query
        for problem, sp in problems_statement_problems.all():
            problem.rank = sp.rank
            problems.append(problem)

        contest.problems = problems

        contest_schema = ContestSchema()

        response = contest_schema.dump(contest)

        return jsonify(response.data)

