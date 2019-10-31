import datetime
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Callable

from informatics_front.utils.run import EjudgeStatuses


PENALTY_TIME_SEC = 20 * 60


class BaseResultMaker(ABC):
    """ Базовый класс для того, что отображается в ячейке монитора """

    is_need_time = False

    def render(self, runs: List[dict], user_id: int) -> dict:
        if self._is_still_testing(runs):
            return self._make_result(
                on_testing=True,
                is_ignored=False,
                mark='',
                time=0,
                success=False,
                wrong_tries=0
            )
        self.update_score_by_statuses(runs)

        wrong_tries = self.get_wrong_tries_count(runs)

        if self._is_last_ignored(runs):
            return self._make_result(
                on_testing=False,
                is_ignored=True,
                mark='',
                time=0,
                success=False,
                wrong_tries=wrong_tries
            )

        mark = self.get_current_mark(runs)
        success = self.is_success(mark)

        return self._make_result(
            on_testing=False,
            is_ignored=False,
            mark=mark,
            time=self.get_time(user_id, runs),
            success=success,
            wrong_tries=wrong_tries
        )

    @classmethod
    def _is_still_testing(cls, runs: List[dict]):
        testing_statuses = (EjudgeStatuses.IN_QUEUE.value,
                            EjudgeStatuses.COMPILING.value,
                            EjudgeStatuses.RUNNING.value)
        return runs[-1]['ejudge_status'] in testing_statuses

    @classmethod
    def _is_last_ignored(cls, runs: List[dict]):
        return runs[-1]['ejudge_status'] == EjudgeStatuses.IGNORED.value

    @classmethod
    def _make_result(cls,
                     on_testing: bool = False,
                     is_ignored: bool = False,
                     mark: str = '',
                     time: int = 0,
                     success: bool = False,
                     wrong_tries: int = 0):
        return {
            'on_testing': on_testing,
            'is_ignored': is_ignored,
            'mark': mark,
            'time': time,
            'success': success,
            'wrong_tries': wrong_tries,
        }

    @abstractmethod
    def update_score_by_statuses(self, runs: List[dict]):
        pass

    @classmethod
    @abstractmethod
    def get_wrong_tries_count(cls, runs: List[dict]):
        pass

    @abstractmethod
    def get_current_mark(self, runs: List[dict]):
        pass

    @abstractmethod
    def is_success(self, runs: List[dict]):
        pass

    @abstractmethod
    def get_time(self, user_id, runs):
        pass


class IOIResultMaker(BaseResultMaker):
    """ Presents IOI-system result of user's runs:
        displaying by solution points (by points) """
    MAX_POINTS = 100

    wrong_statuses = {
        EjudgeStatuses.RE.value,
        EjudgeStatuses.TL.value,
        EjudgeStatuses.PE.value,
        EjudgeStatuses.WA.value,
        EjudgeStatuses.CF.value,
        EjudgeStatuses.PARTIAL.value,
    }

    def is_wrong_status(self, status):
        return status in self.wrong_statuses

    @classmethod
    def update_score_by_statuses(cls, runs):
        """ Changes data inside runs param
            OK -> 100
            PT -> run['ejudge_score']
            otherwise -> 0
        """
        def is_right_status(status_code):
            return status_code == EjudgeStatuses.OK.value or \
                    status_code == EjudgeStatuses.AC.value

        def is_partial(status_code):
            return status_code == EjudgeStatuses.PARTIAL.value

        for run in runs:
            status_code = run['ejudge_status']
            if is_right_status(status_code):
                run['ejudge_score'] = cls.MAX_POINTS
            elif is_partial(status_code):
                # If PT we have the same score
                pass
            else:
                run['ejudge_score'] = 0

    @classmethod
    def get_wrong_tries_count(cls, runs):
        return sum(run['ejudge_status'] in cls.wrong_statuses for run in runs)

    @classmethod
    def get_current_mark(cls, runs: List[dict]) -> str:
        return str(max(run['ejudge_score'] for run in runs))

    @classmethod
    def is_success(cls, mark: str):
        return mark == str(cls.MAX_POINTS)

    def get_time(self, _user_id: int, _runs):
        return 0


class LightACMResultMaker(BaseResultMaker):
    """ Presents ACM-system result of user's runs:
        displaying by success solution (by problem) """

    is_need_time = True

    def __init__(self, get_user_start_time: Callable):
        self.get_user_start_time = get_user_start_time

    wrong_statuses = {
        EjudgeStatuses.RE.value,
        EjudgeStatuses.TL.value,
        EjudgeStatuses.PE.value,
        EjudgeStatuses.WA.value,
        EjudgeStatuses.CF.value,
        EjudgeStatuses.PARTIAL.value,
    }

    def is_wrong_status(self, status: int):
        return status in self.wrong_statuses

    @classmethod
    def update_score_by_statuses(cls, runs):
        """ Score is not changed at ACM """
        pass

    @classmethod
    def get_wrong_tries_count(cls, runs):
        return sum(run['ejudge_status'] in cls.wrong_statuses for run in runs)

    @classmethod
    def get_current_mark(cls, runs: List[dict]) -> str:
        """
        Return
        -----
         AC if any of statuses was AC
         OK if any of statuses was OK
         WA otherwise
        """
        is_ac = any(run['ejudge_status'] == EjudgeStatuses.AC.value for run in runs)
        is_ok = is_ac or any(run['ejudge_status'] == EjudgeStatuses.OK.value for run in runs)
        if is_ac:
            return 'AC'
        if is_ok:
            return 'OK'
        return 'WA'

    @classmethod
    def is_success(cls, mark: str):
        return mark in {'OK', 'AC'}

    def get_time(self, user_id, runs) -> int:
        reversed_runs = reversed(runs)
        first_right_run = None
        for run in reversed_runs:
            if run['ejudge_status'] == EjudgeStatuses.AC.value \
                    or run['ejudge_status'] == EjudgeStatuses.OK.value:
                first_right_run = run
                break

        if first_right_run is None:
            return 0

        delivery_time = datetime\
            .datetime\
            .strptime(first_right_run['create_time'],
                      '%Y-%m-%dT%H:%M:%S%z')

        start_time = self.get_user_start_time(user_id)
        return int((delivery_time - start_time).total_seconds())


class ACMResultMaker(LightACMResultMaker):
    """No custom LightACMResultMaker.get_time
    for appeding penalty time: it's counted on frontned.
    """
    pass


class MonitorPreprocessor:
    """ Превращает сырые данные из мониторов в представление """

    def __init__(self, data: List[dict]):
        self.problem_ids_user_ids_runs = {}
        problem_ids_runs = {d['problem_id']: d['runs'] for d in data}
        for problem_id, runs in problem_ids_runs.items():
            user_ids_runs = self._group_by_users(runs)
            self.problem_ids_user_ids_runs[problem_id] = user_ids_runs

    def get_user_ids(self, problem_ids: List[int]) -> List[int]:
        """ Returns user ids who have at least one run for this problem """
        acc = set()
        for problem_id in problem_ids:
            users_runs = self.problem_ids_user_ids_runs.get(problem_id) or {}
            acc.update(users_runs.keys())
        user_ids = list(acc)

        return user_ids

    def render(self, result_maker: BaseResultMaker) -> dict:
        """
        Returns
        -------
            {
                'user_id1': [
                        'problem_id1': result,
                        'problem_id2': result,
                ],
                'user_id2': ...
            }
        """
        result = defaultdict(dict)
        for problem_id, user_ids_runs in self.problem_ids_user_ids_runs.items():
            for user_id, user_runs in user_ids_runs.items():
                result[user_id][problem_id] = result_maker.render(user_runs, user_id)

        return result

    @classmethod
    def _group_by_users(cls, runs: List[dict]) -> dict:
        """ Group list of runs by users
        Transform:
            [Run1(user=1), Run2(user=2), Run3(user=3), Run4(user=1)]
         ->
            {
                1: [Run1(user=1), Run4(user=1)],
                2: [Run2(user=2)],
                3: [Run3(user=3)],
                ...
            }
        """

        result = defaultdict(list)

        for run in runs:
            result[run['user']['id']].append(run)

        return result
