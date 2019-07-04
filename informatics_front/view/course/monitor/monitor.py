import datetime
from collections import namedtuple, defaultdict
from typing import List, Type, Callable, Optional, Iterable

from flask import request
from flask.views import MethodView
from marshmallow import fields
from sqlalchemy.orm import joinedload, load_only, Load
from webargs.flaskparser import parser
from werkzeug.exceptions import NotFound

from informatics_front.utils.auth.request_user import current_user
from informatics_front.model import db, User, Group, UserGroup, StatementProblem, Problem
from informatics_front.model.contest.contest import Contest
from informatics_front.model.contest.monitor import WorkshopMonitor
from informatics_front.utils.enums import WorkshopMonitorType
from informatics_front.model.workshop.contest_connection import ContestConnection
from informatics_front.model.workshop.workshop import WorkShop, WorkshopStatus
from informatics_front.model.workshop.workshop_connection import WorkshopConnection, WorkshopConnectionStatus
from informatics_front.plugins import internal_rmatics
from informatics_front.utils.auth.middleware import login_required
from informatics_front.utils.response import jsonify
from informatics_front.view.course.monitor.monitor_preprocessor import BaseResultMaker, IOIResultMaker, \
    MonitorPreprocessor, ACMResultMaker, LightACMResultMaker
from informatics_front.view.course.monitor.serializers.monitor import monitor_schema

MonitorData = namedtuple('MonitorData', 'contests users results type')


class WorkshopMonitorApi(MethodView):

    get_args = {
        'group_id': fields.Integer(missing=None)
    }

    @login_required
    def get(self, workshop_id):

        args = parser.parse(self.get_args, request, error_status_code=400)

        if not self._ensure_permissions(workshop_id):
            raise NotFound(f'Monitor for workshop #{workshop_id} is not found')

        monitor: WorkshopMonitor = db.session.query(WorkshopMonitor) \
            .filter(WorkshopMonitor.workshop_id == workshop_id) \
            .first_or_404()

        if not current_user.is_teacher and monitor.is_disabled_for_students():
            raise NotFound(f'Monitor for workshop #{workshop_id} is not found')

        contests = self._get_contests(workshop_id)

        users = self._get_users(monitor, args.get('group_id'))
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

    @classmethod
    def _find_users_on_workshop(cls, workshop_id: int, load_fields: Iterable[str]) -> List[User]:
        """ Returns list of ids of users who has connection to workshop """
        users = db.session.query(User) \
            .join(WorkshopConnection) \
            .filter(WorkshopConnection.workshop_id == workshop_id) \
            .options(load_only(*load_fields)) \
            .all()

        return users

    @classmethod
    def _find_users_by_group(cls, group_id: int, load_fields: Iterable[str]) -> List[User]:
        users = db.session.query(User).join(UserGroup).join(Group).filter(Group.id == group_id) \
            .options(load_only(*load_fields)) \
            .all()
        return users

    @classmethod
    def _get_users(cls, monitor, group_id: Optional[int]) -> List[User]:
        load_only_fields = ('firstname', 'lastname', 'city', 'school', )
        if not current_user.is_teacher and monitor.is_for_user_only():
            users = [db.session.query(User).get(current_user.id)]
        elif group_id is not None:
            users = cls._find_users_by_group(group_id, load_only_fields)
        else:
            users = cls._find_users_on_workshop(monitor.workshop_id, load_only_fields)

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
        contests: List[Contest] = db.session.query(Contest)\
            .filter(Contest.workshop_id == workshop_id)\
            .options(joinedload(Contest.statement))

        statement_ids = [contest.statement.id for contest in contests]

        statement_problems: List[StatementProblem] = db.session.query(StatementProblem) \
            .filter(StatementProblem.statement_id.in_(statement_ids)) \
            .filter(StatementProblem.problem_id.isnot(None)) \
            .options(joinedload(StatementProblem.problem).load_only('id', 'name')) \
            .options(Load(StatementProblem).load_only('statement_id', 'rank')) \
            .options(Load(Problem).load_only('id', 'name'))

        # Filter statement problems with removed problems
        statement_problems = [sp
                              for sp in statement_problems
                              if sp.problem is not None]

        for sp in statement_problems:
            sp.problem.rank = sp.rank

        statement_id_statement_problems = defaultdict(list)

        for sp in statement_problems:
            statement_id_statement_problems[sp.statement_id].append(sp.problem)

        for contest in contests:
            statement_id = contest.statement_id
            problems = statement_id_statement_problems[statement_id]
            contest.problems = problems

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
        runs_until = runs_until and int(runs_until.timestamp())

        data, _ = internal_rmatics.get_monitor(problem_ids,
                                               user_ids,
                                               runs_until)
        return data

    @classmethod
    def _make_start_time_retriever(cls, contest, user_ids: List[int]) -> Callable:
        """
        Returns function for getting contest start time by user_id
        """
        if not contest.is_virtual:
            start_time = contest.time_start or contest.created_at

            def const_time(*__, **___):
                return start_time.astimezone()

            return const_time

        user_id_time = {}
        created_time_user_id_q = db.session.query(ContestConnection.created_at,
                                                  ContestConnection.user_id) \
            .filter(ContestConnection.user_id.in_(user_ids))
        for created_time, user_id in created_time_user_id_q:
            user_id_time[user_id] = created_time

        def time_by_cc(user_id: int):
            time = user_id_time.get(user_id) or datetime.datetime.utcfromtimestamp(0)
            return time.astimezone()

        return time_by_cc

    @classmethod
    def _prepare_data(cls, monitor: WorkshopMonitor, contest: Contest, raw_data: List[dict]) -> dict:
        monitor_processor = MonitorPreprocessor(raw_data)

        result_maker_cls = cls._get_result_maker_cls(monitor)
        if result_maker_cls.is_need_time:
            problem_ids = cls._extract_problem_ids([contest])
            user_ids = monitor_processor.get_user_ids(problem_ids)
            get_user_start_time = cls._make_start_time_retriever(contest, user_ids)
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
            WorkshopMonitorType.LightACM: LightACMResultMaker
        }

        return result_maker_map[monitor.type]
