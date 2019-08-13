from typing import List

from flask import request
from flask.views import MethodView
from marshmallow import fields
from webargs.flaskparser import parser
from werkzeug.exceptions import NotFound, BadRequest, Forbidden

from informatics_front.model import db, LanguageContest
from informatics_front.model.problem import EjudgeProblem
from informatics_front.model.workshop.contest_connection import ContestConnection
from informatics_front.plugins import internal_rmatics
from informatics_front.utils.auth.middleware import login_required
from informatics_front.utils.auth.request_user import current_user
from informatics_front.utils.response import jsonify
from informatics_front.view.course.contest.serializers.problem import ProblemSchema


def check_contest_connection(contest_id, error_obj: Exception) -> ContestConnection:
    cc = db.session.query(ContestConnection) \
        .filter_by(user_id=current_user.id, contest_id=contest_id) \
        .one_or_none()
    if cc is None:
        raise error_obj
    return cc


def check_contest_languages(contest_id: int, language_id: int, error_obj: Exception) -> None:
    """Check if language can be used for contest submittions

    If contest is not language-aware (no languages are set for this contest),
    allow submittions with any language.

    :param contest_id: Contest ID, for which we check permissions.
    :param language_id: Language ID, for witch we check permissions.
    :param error_obj: Error to raise, if using provided language_id is prohibited.
    :return: None
    """
    lcs: List[LanguageContest] = db.session.query(LanguageContest) \
        .filter_by(contest_id=contest_id) \
        .all()

    # Non languages-aware contest. All languages allowed
    if not lcs:
        return None

    # If language_id is allowed for this contest
    lcs = [lc for lc in lcs if lc.language_id == language_id]
    if not lcs:
        raise error_obj


class ProblemApi(MethodView):
    @login_required
    def get(self, contest_id, problem_id):
        check_contest_connection(contest_id,
                                 NotFound(f'Problem with id #{problem_id} is not found or '
                                          f'you don\'t have permissions to participate'))

        problem = db.session.query(EjudgeProblem).filter_by(id=problem_id).one_or_none()
        if problem is None:
            raise NotFound(f'Problem with id #{problem_id} is not found or '
                           f'you don\'t have permissions to participate')

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
    def post(self, contest_id, problem_id):
        check_contest_connection(contest_id, NotFound(f'Problem with id #{problem_id} is not found or '
                                                      f'you don\'t have permissions to participate'))
        args = parser.parse(self.post_args, request)
        check_contest_languages(contest_id, args.get('lang_id'), Forbidden('This language is forbidden '
                                                                           'for solving problems for this contest. '
                                                                           'Please, use another language.'))
        file = request.files.get('file')
        if file is None:
            raise BadRequest('Parameter \'file\' is not fulfilled')

        content, status = internal_rmatics.send_submit(file,
                                                       current_user.id,
                                                       problem_id,
                                                       contest_id,
                                                       args['statement_id'],
                                                       args['lang_id'])
        return jsonify(content, status_code=status)

    @login_required
    def get(self, contest_id, problem_id):
        check_contest_connection(contest_id,
                                 NotFound(f'Problem with id #{problem_id} is not found or '
                                          f'you don\'t have permissions to participate'))

        args = parser.parse(self.get_args, request, error_status_code=400)

        # set current authorized user to args
        args['user_id'] = current_user.id

        content, status = internal_rmatics.get_runs_filter(problem_id, contest_id, args)
        return jsonify(content, status_code=status)
