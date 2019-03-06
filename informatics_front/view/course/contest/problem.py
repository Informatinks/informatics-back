from flask import request, g
from flask.views import MethodView
from marshmallow import fields, missing
from sqlalchemy.orm import joinedload
from webargs.flaskparser import parser
from werkzeug.exceptions import NotFound, BadRequest

from informatics_front import internal_rmatics
from informatics_front.model import db, Problem
from informatics_front.utils.auth import login_required
from informatics_front.utils.response import jsonify
from informatics_front.view.course.contest.serializers.problem import ProblemSchema


class ProblemApi(MethodView):
    @login_required
    def get(self, problem_id):
        problem = db.session.query(Problem) \
            .options(joinedload(Problem.ejudge_problem)) \
            .get(problem_id)
        if problem is None:
            raise NotFound(f'Problem with id #{problem_id} is not found')

        problem_serializer = ProblemSchema()

        response = problem_serializer.dump(problem)

        return jsonify(response.data)


class ProblemSubmissionApi(MethodView):
    get_args = {
        'group_id': fields.Integer(),
        'lang_id': fields.Integer(),
        'status_id': fields.Integer(),
        'statement_id': fields.Integer(),
        'count': fields.Integer(default=10, missing=10),
        'page': fields.Integer(default=1, missing=1),
        'from_timestamp': fields.Integer(),
        'to_timestamp': fields.Integer(),
    }

    post_args = {
        'lang_id': fields.Integer(required=True),
        'statement_id': fields.Integer(missing=None),
    }

    @login_required
    def post(self, problem_id):
        user_id = g.user['id']
        args = parser.parse(self.post_args, request)
        file = parser.parse_files(request, 'file', 'file')

        if file is missing:
            raise BadRequest('Parameter \'file\' is not fulfilled')

        content, status = internal_rmatics.send_submit(file,
                                                       user_id,
                                                       problem_id,
                                                       args['statement_id'],
                                                       args['lang_id'])
        return jsonify(content, status_code=status)

    @login_required
    def get(self, problem_id):
        args = parser.parse(self.get_args, request, error_status_code=400)
        content, status = internal_rmatics.get_runs_filter(problem_id, args, is_admin=False)
        return jsonify(content, status_code=status)
