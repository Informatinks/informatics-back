from typing import Optional

from flask import g
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Load, joinedload
from werkzeug.exceptions import NotFound

from informatics_front.model import Problem, StatementProblem
from informatics_front.model.base import db
from informatics_front.model.contest.contest_instance import ContestInstance
from informatics_front.model.workshop.contest_connection import ContestConnection
from informatics_front.model.workshop.workshop_connection import WorkshopConnection, WorkshopConnectionStatus
from informatics_front.utils.auth import login_required
from informatics_front.utils.response import jsonify
from informatics_front.view.course.contest.serializers.contest import ContestSchema


class ContestApi(MethodView):
    @login_required
    def get(self, contest_instance_id):
        contest_instance = db.session.query(ContestInstance) \
                            .options(joinedload(ContestInstance.contest)) \
                            .options(joinedload(ContestInstance.workshop)) \
                            .get(contest_instance_id)

        if contest_instance is None:
            raise NotFound(f'Cannot find contest module id #{contest_instance_id}')

        user_id = g.user['id']
        self._check_workshop_permissions(user_id,
                                         contest_instance.workshop)

        cc = self._get_contest_connection(user_id, contest_instance.id)
        if cc is None:
            # TODO: check contest_instance permissions
            self._create_contest_connection(user_id, contest_instance.id)

        problems_statement_problems = db.session.query(Problem, StatementProblem) \
            .join(StatementProblem, StatementProblem.problem_id == Problem.id) \
            .filter(StatementProblem.statement_id == contest_instance.contest_id) \
            .filter(StatementProblem.hidden == 0) \
            .options(Load(Problem).load_only('id', 'name')) \
            .options(Load(StatementProblem).load_only('rank'))

        contest = contest_instance.contest

        problems = []
        # Yes it is ugly but I think its better than rewrite query
        for problem, sp in problems_statement_problems.all():
            problem.rank = sp.rank
            problems.append(problem)

        contest.problems = problems

        contest_schema = ContestSchema()

        response = contest_schema.dump(contest)

        return jsonify(response.data)

    @classmethod
    def _check_workshop_permissions(cls, user_id, workshop) -> Optional[WorkshopConnection]:
        workshop_connection = db.session.query(WorkshopConnection) \
                                        .filter_by(user_id=user_id,
                                                   workshop_id=workshop.id) \
                                        .one_or_none()
        if workshop_connection is None or \
                workshop_connection.status != WorkshopConnectionStatus.ACCEPTED:
            raise NotFound('Contest is not found')

        return workshop_connection

    @classmethod
    def _get_contest_connection(cls, user_id: int, contest_instance_id: int) -> ContestConnection:
        cc = db.session.query(ContestConnection) \
            .filter_by(user_id=user_id, contest_instance_id=contest_instance_id) \
            .one_or_none()
        return cc

    @classmethod
    def _create_contest_connection(cls, user_id, contest_instance_id: int):
        cc = ContestConnection(user_id=user_id, contest_instance_id=contest_instance_id)
        db.session.begin_nested()
        try:
            db.session.add(cc)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            cc = cls._get_contest_connection(user_id, contest_instance_id)  # 7)
        return cc
