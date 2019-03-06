from flask import g
from flask.views import MethodView

from informatics_front import internal_rmatics
from informatics_front.utils.auth import login_required
from informatics_front.utils.response import jsonify


PROTOCOL_EXCLUDE_FIELDS = ['audit']
PROTOCOL_EXCLUDE_TEST_FIELDS = [
    'input', 'big_input', 'corr',
    'big_corr', 'output', 'big_output',
    'checker_output', 'error_output', 'extra'
]


class RunSourceApi(MethodView):
    @login_required
    def get(self, run_id):
        user_id = g.user['id']
        context, status = internal_rmatics.get_run_source(run_id, user_id)

        return jsonify(context, status_code=status)


class RunProtocolApi(MethodView):
    @login_required
    def get(self, run_id: int):
        user_id = g.user['id']
        context, status = internal_rmatics.get_full_run_protocol(run_id, user_id)

        if status > 299:
            return jsonify(context, status_code=status)

        protocol = self._remove_fields_from_full_protocol(context)

        return jsonify(protocol, status_code=status)

    @classmethod
    def _remove_fields_from_full_protocol(cls, protocol):
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
