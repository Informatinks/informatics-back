from typing import Tuple

from informatics_front.utils.services.base import ApiClient, BaseService


class InternalRmatics(BaseService):
    service_url_param = 'INTERNAL_RMATICS_URL'
    default_service_url = 'http://localhost:12346'

    def __init__(self, timeout: int = 60, logger=None):
        self.service_url = None
        self.client = ApiClient(timeout=timeout, logger=logger)

    def send_submit(self, file,
                    user_id: int,
                    problem_id: int,
                    statement_id: int,
                    lang_id: int) -> Tuple[dict, int]:
        data = {
            'lang_id': lang_id,
            'user_id': user_id,
            'statement_id': statement_id
        }
        url = self.service_url + f'/problem/trusted/{problem_id}/submit_v2'

        content, status = self.client.post_data(url, json=data, files={'file': file}, silent=True)
        return content, status

    def get_runs_filter(self, problem_id: int,
                        args: dict,
                        is_admin=False) -> Tuple[dict, int]:
        filter_args = {
            **args,
            'is_admin': is_admin,
        }
        url = self.service_url + f'/problem/{problem_id}/submissions/'
        content, status = self.client.get_data(url, params=filter_args, silent=True, default=[])

        return content, status
