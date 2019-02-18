from flask.views import MethodView
from werkzeug.exceptions import NotFound

from informatics_front.model import db, Problem
from informatics_front.utils.auth import login_required
from informatics_front.utils.response import jsonify
from informatics_front.view.course.contest.serializers.problem import ProblemSchema


class ProblemApi(MethodView):
    @login_required
    def get(self, problem_id):
        problem = db.session.query(Problem).get(problem_id)
        if problem is None:
            raise NotFound(f'Problem with id #{problem_id} is not found')

        problem_serializer = ProblemSchema()

        response = problem_serializer.dump(problem)

        return jsonify(response.data)

