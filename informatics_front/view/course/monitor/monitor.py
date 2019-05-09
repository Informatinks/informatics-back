from typing import List

from flask.views import MethodView

from informatics_front import current_user
from informatics_front.model import db, Problem, Statement, StatementProblem
from informatics_front.model.contest.contest import Contest
from informatics_front.model.contest.monitor import WorkshopMonitor
from informatics_front.model.workshop.workshop import WorkShop
from informatics_front.model.workshop.workshop_connection import WorkshopConnection
from informatics_front.plugins import internal_rmatics
from informatics_front.utils.auth import login_required
from informatics_front.utils.response import jsonify


class WorkshopMonitorApi(MethodView):

    @classmethod
    def _find_users_on_workshop(cls, workshop_id: int) -> List[int]:
        """ Returns list of ids of users who has connection to workshop """
        user_ids = db.session.query(WorkshopConnection.user_id) \
            .filter(WorkshopConnection.workshop_id == workshop_id) \
            .all()

        return [user_id[0] for user_id in user_ids]

    @classmethod
    def _find_problems(cls, workshop_id) -> List[int]:
        """ Returns list of ids of problems in this contest """
        problem_ids = db.session.query(Problem.id) \
            .join(StatementProblem) \
            .join(Statement) \
            .join(Contest) \
            .join(WorkShop) \
            .filter(WorkShop.id == workshop_id)

        return [problem_id[0] for problem_id in problem_ids]

    @login_required
    def get(self, workshop_id):
        monitor: WorkshopMonitor = db.session.query(WorkshopMonitor) \
            .filter(WorkshopMonitor.workshop_id == workshop_id) \
            .first_or_404()

        if not current_user.is_teacher and monitor.is_for_user_only():
            user_ids = [current_user.id]
        else:
            user_ids = self._find_users(workshop_id)

        problem_ids = self._find_problems(workshop_id)

        data = internal_rmatics.get_monitor(problem_ids,
                                            user_ids,
                                            monitor.freeze_time.utctimestamp())

        return jsonify(data.get('data'))

