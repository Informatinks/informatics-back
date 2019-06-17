from typing import Tuple, Optional, List

from werkzeug.datastructures import FileStorage

from informatics_front.utils.services.base import BaseService


class InternalRmatics(BaseService):
    service_url_param = 'INTERNAL_RMATICS_URL'
    default_timeout = 60
    context_source = 2

    def send_submit(self,
                    file: FileStorage,
                    user_id: int,
                    problem_id: int,
                    contest_id: int,
                    statement_id: int,
                    lang_id: int) -> Tuple[dict, int]:
        data = {
            'lang_id': lang_id,
            'user_id': user_id,
            'statement_id': statement_id,
            'context_id': contest_id,
            'context_source': self.context_source,
            'is_visible': False,

        }
        url = f'{self.service_url}/problem/trusted/{problem_id}/submit_v2'

        return self.client.post_data(url, json=data, files={'file': file.stream}, silent=True)

    def get_runs_filter(self, problem_id: int, contest_id: int, args: dict) -> Tuple[dict, int]:
        filter_args = {
            **args,
            'context_id': contest_id,
            'context_source': self.context_source,
            'is_visible': False,
        }
        url = f'{self.service_url}/problem/{problem_id}/submissions/'

        return self.client.get_data(url, params=filter_args, silent=True, default=[])

    def get_run_source(self, run_id: int, user_id, is_admin: bool = False) -> Tuple[dict, int]:
        url = f'{self.service_url}/problem/run/{run_id}/source/'

        user_args = {
            'user_id': user_id,
            'is_admin': is_admin,
        }

        return self.client.get_data(url, params=user_args, silent=True)

    def get_full_run_protocol(self, run_id: int, user_id: int, is_admin: bool = False) -> Tuple[dict, int]:
        url = f'{self.service_url}/problem/run/{run_id}/protocol'

        user_args = {
            'user_id': user_id,
            'is_admin': is_admin,
        }

        return self.client.get_data(url, params=user_args, silent=True)

    def get_monitor(self, problems: List[int], users: List[int], time_before: Optional[int]):
        # TODO: Приделать контекст посылки (NFRMTCS-192)
        url = f'{self.service_url}/monitor/problem_monitor'

        monitor_args = {
            'user_id': users,
            'problem_id': problems
        }
        if time_before:
            monitor_args['time_before'] = time_before

        return self.client.get_data(url, params=monitor_args, silent=True, default=[])
