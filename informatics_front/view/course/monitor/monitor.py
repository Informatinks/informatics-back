import datetime
from collections import namedtuple
from typing import List, Type, Callable

from flask.views import MethodView
from sqlalchemy.orm import joinedload, load_only
from werkzeug.exceptions import NotFound

from informatics_front import current_user
from informatics_front.model import db, Statement, User
from informatics_front.model.contest.contest import Contest
from informatics_front.model.contest.monitor import WorkshopMonitor, WorkshopMonitorType
from informatics_front.model.workshop.contest_connection import ContestConnection
from informatics_front.model.workshop.workshop import WorkShop, WorkshopStatus
from informatics_front.model.workshop.workshop_connection import WorkshopConnection, WorkshopConnectionStatus
from informatics_front.plugins import internal_rmatics
from informatics_front.utils.auth import login_required
from informatics_front.utils.response import jsonify
from informatics_front.view.course.monitor.monitor_preprocessor import BaseResultMaker, IOIResultMaker, \
    MonitorPreprocessor, ACMResultMaker
from informatics_front.view.course.monitor.serializers.monitor import monitor_schema

MonitorData = namedtuple('MonitorData', 'contests users results type')


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
    def _get_raw_data_by_contest(cls, monitor: WorkshopMonitor, user_ids: List[int], contest: Contest):
        problem_ids = cls._extract_problem_ids([contest])

        runs_until = monitor.freeze_time
        runs_until = runs_until and runs_until.utctimestamp()

        data, _ = internal_rmatics.get_monitor(problem_ids,
                                               user_ids,
                                               runs_until)
        return data

    @classmethod
    def _make_function_getting_user_start_time(cls, contest, user_ids: List[int]) -> Callable:
        """
        Returns function for getting contest start time by user_id
        """
        if not contest.is_virtual:
            start_time = contest.time_start or contest.created_at

            def const_time(*__, **___):
                return start_time

            return const_time

        user_id_time = {}
        created_time_user_id_q = db.session.query(ContestConnection.created_at,
                                                  ContestConnection.user_id) \
            .filter(ContestConnection.user_id.in_(user_ids))
        for created_time, user_id in created_time_user_id_q:
            user_id_time[user_id] = created_time

        def time_by_cc(user_id: int):
            time = user_id_time.get(user_id)
            return time or datetime.datetime.utcfromtimestamp(0)

        return time_by_cc

    @classmethod
    def _prepare_data(cls, monitor: WorkshopMonitor, contest: Contest, raw_data: List[dict]) -> dict:
        monitor_processor = MonitorPreprocessor(raw_data)

        result_maker_cls = cls._get_result_maker_cls(monitor)
        if result_maker_cls.is_need_time:
            problem_ids = cls._extract_problem_ids([contest])
            user_ids = monitor_processor.get_user_ids(problem_ids)
            get_user_start_time = cls._make_function_getting_user_start_time(contest, user_ids)
            result_maker = result_maker_cls(get_user_start_time)
        else:
            result_maker = result_maker_cls()

        data = monitor_processor.render(result_maker)

        return data

    @classmethod
    def _get_result_maker_cls(cls, monitor: WorkshopMonitor) -> Type[BaseResultMaker]:
        result_maker_map = {
            WorkshopMonitorType.ACM: ACMResultMaker,
            WorkshopMonitorType.IOI: IOIResultMaker,
            WorkshopMonitorType.LightACM: ACMResultMaker
        }

        return result_maker_map[monitor.type]

    @login_required
    def get(self, workshop_id):

        if not self._ensure_permissions(workshop_id):
            raise NotFound(f'Monitor for workshop #{workshop_id} is not found')

        monitor: WorkshopMonitor = db.session.query(WorkshopMonitor) \
            .filter(WorkshopMonitor.workshop_id == workshop_id) \
            .first_or_404()

        if not current_user.is_teacher and monitor.is_disabled_for_students():
            raise NotFound(f'Monitor for workshop #{workshop_id} is not found')

        contests = self._get_contests(workshop_id)

        users = self._get_users(monitor)
        user_ids = [user.id for user in users]

        results = []
        for contest in contests:
            raw_data = self._get_raw_data_by_contest(monitor, user_ids, contest)
            data = self._prepare_data(monitor, contest, raw_data)
            results.append({
                'contest_id': contest.id,
                'results': data
            })

        monitor_data = MonitorData(contests, users, results, monitor.type.name)

        data = monitor_schema.dump(monitor_data)

        return jsonify(data.data)

