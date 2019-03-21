from typing import Tuple

from informatics_front.utils.services.base import ApiClient, BaseService
from werkzeug.datastructures import FileStorage


class InternalRmatics(BaseService):
    service_url_param = 'INTERNAL_RMATICS_URL'
    default_timeout = 60

    def send_submit(self,
                    file: FileStorage,
                    user_id: int,
                    problem_id: int,
                    statement_id: int,
                    lang_id: int) -> Tuple[dict, int]:
        data = {
            'lang_id': lang_id,
            'user_id': user_id,
            'statement_id': statement_id
        }
        url = f'{self.service_url}/problem/trusted/{problem_id}/submit_v2'

        return self.client.post_data(url, json=data, files={'file': file.stream}, silent=True)

    def get_runs_filter(self, problem_id: int,
                        args: dict,
                        is_admin=False) -> Tuple[dict, int]:
        filter_args = {
            **args,
            'is_admin': is_admin,
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
