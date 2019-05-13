from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List

from informatics_front.utils.run import EjudgeStatuses


class BaseResultMaker(ABC):
    """ Базовый класс для того, что отображается в ячейке монитора """

    def render(self, runs: List[dict]) -> dict:
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
            time=0,
            success=success,
            wrong_tries=wrong_tries
        )

    @classmethod
    def _is_still_testing(cls, runs: List[dict]):
        testing_statuses = (EjudgeStatuses.IN_QUEUE.value,
                            EjudgeStatuses.COMPILING.value,
                            EjudgeStatuses.RUNNING.value)
        return any(run['ejudge_status'] in testing_statuses for run in runs)

    @classmethod
    def _is_last_ignored(cls, runs: List[dict]):
        return runs[-1]['ejudge_status'] == EjudgeStatuses.IGNORED.value

    @classmethod
    def _make_result(cls,
                     on_testing: bool = False,
                     is_ignored: bool = False,
                     mark: str = '',
                     time: int =0,
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


# class ACMResultMaker(BaseResultMaker):
#     """ Presents ACM-system result of user's runs:
#         displaying by success solution (by problem) """
#
#     wrong_statuses = {
#         EjudgeStatuses.RE.value,
#         EjudgeStatuses.TL.value,
#         EjudgeStatuses.PE.value,
#         EjudgeStatuses.WA.value,
#         EjudgeStatuses.CF.value,
#         EjudgeStatuses.PARTIAL.value,
#     }
#     pass


class MonitorPreprocessor:
    """ Превращает сырые данные из мониторов в представление """
    def __init__(self):
        pass

    def render(self, data, result_maker: BaseResultMaker):
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
        problem_ids_runs = {d['problem']['id']: d['runs'] for d in data}
        for problem_id, runs in problem_ids_runs.items():
            user_ids_runs = self._group_by_users(runs)
            for user_id, user_runs in user_ids_runs.items():
                result[user_id][problem_id] = result_maker.render(user_runs)

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
