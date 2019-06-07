from flask.views import MethodView
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import BadRequest, NotFound

from informatics_front.model.contest.contest import Contest, ContestProtocolVisibility
from informatics_front.utils.auth.request_user import current_user
from informatics_front.plugins import internal_rmatics
from informatics_front.model import Comment, Statement, StatementProblem
from informatics_front.model.base import db
from informatics_front.utils.auth.middleware import login_required
from informatics_front.utils.response import jsonify
from informatics_front.view.course.contest.serializers.comment import CommentSchema

PROTOCOL_EXCLUDE_FIELDS = ['audit']
PROTOCOL_EXCLUDE_TEST_FIELDS = [
    'input', 'big_input', 'corr',
    'big_corr', 'output', 'big_output',
    'checker_output', 'error_output', 'extra'
]


class RunSourceApi(MethodView):
    @login_required
    def get(self, run_id):
        context, status = internal_rmatics.get_run_source(run_id, current_user.id)

        return jsonify(context, status_code=status)


class RunProtocolApi(MethodView):
    @login_required
    def get(self, contest_id: int, problem_id: int, run_id: int):
        contest_visibility = db.session.query(Contest.protocol_visibility) \
            .filter_by(id=contest_id).join(Statement) \
            .join(StatementProblem) \
            .filter(StatementProblem.problem_id == problem_id) \
            .one_or_none()

        if contest_visibility is None:
            raise BadRequest('Bad protocol_id or problem_id')

        contest_visibility = contest_visibility and contest_visibility[0]

        if contest_visibility is ContestProtocolVisibility.INVISIBLE:
            raise NotFound('Protocol for current')

        context, status = internal_rmatics.get_full_run_protocol(run_id, current_user.id)

        if status > 299:
            return jsonify(context, status_code=status)

        # TODO: NFRMTCS-192: нужен контекст,
        # TODO: чтобы нельзя было смотреть любой протокол, найдя открытый воркшоп
        protocol = self._remove_fields_from_full_protocol(context)

        if contest_visibility is ContestProtocolVisibility.FIRST_BAD_TEST:
            protocol = self._remove_all_after_bad_test(protocol)

        return jsonify(protocol, status_code=status)

    @classmethod
    def _remove_fields_from_full_protocol(cls, protocol: dict) -> dict:
        # We need to remove some fields for student
        for field in PROTOCOL_EXCLUDE_FIELDS:
            protocol.pop(field, None)

        tests = protocol.get('tests')

        if not tests:
            return protocol

        for test in tests.values():
            for field in PROTOCOL_EXCLUDE_TEST_FIELDS:
                test.pop(field, None)

        return protocol

    @classmethod
    def _remove_all_after_bad_test(cls, protocol: dict) -> dict:
        """ Returns protocol where we have only first failed test """
        tests = protocol.get('tests')
        sorted_tests = list(sorted(tests.items(), key=lambda t: int(t[0])))
        visible_tests = {}
        for k, v in sorted_tests:
            visible_tests[k] = v
            if v.get('status') != 'OK':
                break
        protocol['tests'] = visible_tests
        return protocol


class RunCommentsApi(MethodView):
    @login_required
    def get(self, run_id):
        """
        Returns List[Comment] for current authorized user for requested run_id
        """

        # if provided run_id not not found, return []
        comments = db.session.query(Comment) \
            .filter(Comment.py_run_id == run_id,
                    Comment.user_id == current_user.id) \
            .options(joinedload(Comment.author_user)) \
            .order_by(Comment.date.desc()) \
            .all()

        comment_schema = CommentSchema(many=True)
        response = comment_schema.dump(comments)

        return jsonify(response.data)
