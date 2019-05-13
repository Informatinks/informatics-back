from collections import namedtuple
from typing import List, Type

from flask.views import MethodView
from sqlalchemy.orm import joinedload, load_only
from werkzeug.exceptions import NotFound

from informatics_front import current_user
from informatics_front.model import db, Statement, User
from informatics_front.model.contest.contest import Contest
from informatics_front.model.contest.monitor import WorkshopMonitor
from informatics_front.model.workshop.workshop import WorkShop, WorkshopStatus
from informatics_front.model.workshop.workshop_connection import WorkshopConnection, WorkshopConnectionStatus
from informatics_front.plugins import internal_rmatics
from informatics_front.utils.auth import login_required
from informatics_front.utils.response import jsonify
from informatics_front.view.course.monitor.monitor_preprocessor import BaseResultMaker, IOIResultMaker, \
    MonitorPreprocessor
from informatics_front.view.course.monitor.serializers.monitor import monitor_schema

MonitorData = namedtuple('MonitorData', 'contests users results')


class WorkshopMonitorApi(MethodView):

    @classmethod
    def _find_users_on_workshop(cls, workshop_id: int) -> List[User]:
        """ Returns list of ids of users who has connection to workshop """
        users = db.session.query(User) \
            .join(WorkshopConnection) \
            .filter(WorkshopConnection.workshop_id == workshop_id) \
            .options(load_only('id', 'firstname', 'lastname')) \
            .all()

        return users

    @classmethod
    def _get_users(cls, monitor) -> List[User]:
        if not current_user.is_teacher and monitor.is_for_user_only():
            users = [User(id=current_user.id,
                          firstname=current_user.firstname,
                          lastname=current_user.lastname)]
        else:
            users = cls._find_users_on_workshop(monitor.workshop_id)

        return users

    @classmethod
    def _extract_problem_ids(cls, contests: List[Contest]) -> List[int]:
        """ Returns list of ids of problems in this contests """
        problem_ids = []
        for contest in contests:
            ids = [p.id for p in contest.statement.problems]
            problem_ids += ids

        return problem_ids

    @classmethod
    def _get_contests(cls, workshop_id):
        contests: List[Contest] = db.session.query(Contest) \
            .filter(Contest.workshop_id == workshop_id) \
            .options(joinedload(Contest.statement)
                     .joinedload(Statement.problems)) \
            .all()

        return contests

    @classmethod
    def _ensure_permissions(cls, workshop_id) -> bool:
        if current_user.is_teacher:
            return True

        return db.session.query(WorkshopConnection) \
            .filter(WorkshopConnection.workshop_id == workshop_id,
                    WorkshopConnection.user_id == current_user.id,
                    WorkshopConnection.status == WorkshopConnectionStatus.ACCEPTED,
                    WorkShop.status == WorkshopStatus.ONGOING) \
            .one_or_none()

    @classmethod
    def _get_raw_monitor_data(cls, monitor: WorkshopMonitor, user_ids: List[int], problem_ids: List[int]) -> List[dict]:

        runs_until = monitor.freeze_time
        runs_until = runs_until and runs_until.utctimestamp()

        data, _ = internal_rmatics.get_monitor(problem_ids,
                                               user_ids,
                                               runs_until)
        return data

    @classmethod
    def _get_result_maker_cls(cls, _monitor: WorkshopMonitor) -> Type[BaseResultMaker]:
        # TODO: ACM & lightACM
        return IOIResultMaker

    @login_required
    def get(self, workshop_id):

        if not self._ensure_permissions(workshop_id):
            raise NotFound(f'Monitor for workshop #{workshop_id} is not found')

        monitor: WorkshopMonitor = db.session.query(WorkshopMonitor) \
            .filter(WorkshopMonitor.workshop_id == workshop_id) \
            .first_or_404()

        contests = self._get_contests(workshop_id)
        problem_ids = self._extract_problem_ids(contests)

        users = self._get_users(monitor)
        user_ids = [user.id for user in users]

        raw_data = self._get_raw_monitor_data(monitor, user_ids, problem_ids)

        result_maker_cls = self._get_result_maker_cls(monitor)
        processor = MonitorPreprocessor()
        results = processor.render(raw_data, result_maker_cls())

        monitor_data = MonitorData(contests, users, results)

        data = monitor_schema.dump(monitor_data)

        return jsonify(data.data)

