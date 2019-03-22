import inspect
import logging
from typing import Tuple

import requests

from informatics_front.utils.services.errors import ClientError, ServerError


class ApiClient(requests.Session):
    """Base class for API clients."""

    def __init__(self,
                 timeout=60,
                 tracer=None,
                 logger: logging.Logger = None):

        super().__init__()

        self.tracer = tracer
        self.timeout = timeout
        self.logger = logger

        # When Flask app logger is not passed
        if not logger:
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.setLevel(logging.ERROR)

        request_method_signature = inspect.signature(self.request)
        self._allowed_kwargs = set(request_method_signature.parameters.keys())

    def _request(self, url, method='GET', json=None, data_key=None,
                 default=None, silent=False, allow_bad_http_statuses=True, **kwargs) -> Tuple[dict, int]:
        """Wrap self.request method."""
        kwargs = {**kwargs, 'timeout': self.timeout}
        headers = {
            **self.headers,
            **kwargs.pop('headers', {})
        }

        # set payload data key based on files persistence
        if method in ('POST', 'PUT', 'PATCH'):
            if kwargs.get('files'):  # and kwargs['files'] to check empty file payload
                kwargs['data'] = json
            else:
                kwargs['json'] = json

        if self.tracer:
            # Creates tracing header
            headers.update(self.tracer.headers)

        clean_kwargs = {
            key: value for key, value in kwargs.items()
            if key in self._allowed_kwargs
        }

        try:
            response = self.request(method, url,
                                    headers=headers,
                                    **clean_kwargs)
        except requests.RequestException:
            self.logger.exception(
                f'Unable to get data from {url}. \n'
                f'Kwargs: {clean_kwargs}. '
                f'Passed kwargs: {kwargs}'
            )

            if not silent:
                raise ServerError()
            return default, 500

        if not allow_bad_http_statuses:
            if 400 <= response.status_code < 500:
                self.logger.error(f'URL: {url}.\n Response: {response.content}')
                if not silent:
                    raise ClientError(response.status_code)
                return default, response.status_code

            if 500 <= response.status_code < 600:
                self.logger.exception(
                    f'Server error returned when sending request to "{url}". '
                    f'Got response: "{str(response.content)}"'
                )

                if not silent:
                    raise ServerError()
                return default, response.status_code

        data_key = data_key if data_key else 'data'

        if allow_bad_http_statuses and response.status_code >= 400:
            data_key = 'error'

        json_response = response.json()[data_key]
        return json_response, response.status_code

    def put_data(self, url, json, default=None,
                 silent=False, data_key=None, **kwargs):
        return self._request(url, method='PUT', json=json,
                             data_key=data_key, default=default,
                             silent=silent, **kwargs)

    def post_data(self, url, data=None, json=None, default=None,
                  silent=False, data_key=None, **kwargs):
        return self._request(url, method='POST', data=data, json=json,
                             data_key=data_key, default=default,
                             silent=silent, **kwargs)

    def get_data(self, url, data_key=None, default=None,
                 silent=False, **kwargs):
        return self._request(url, method='GET', data_key=data_key,
                             default=default, silent=silent, **kwargs)


class BaseService:
    """Base service extension.

    Usage for children classes:
        # plugins.py
        users_service = UsersServiceV1()

        # app_factory.py

        app = Flask()
        tracer.init_app(app)
        users_service.init_app(app)


        # views.py
        from plugins import users_service
        ...
        def get(self, user_id):
            result = users_service.get_user(user_id)
            return result
    """
    default_timeout = 5 * 60

    def __init__(self, app=None, timeout=None, tracer=None, logger=None):
        self.client = ApiClient(timeout or self.default_timeout, tracer, logger)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Configure service settings based on flask app config."""
        self.service_url = app.config.get(self.service_url_param)

        @app.teardown_appcontext
        def shutdown_apiclient(response_or_exc):
            if self.client is not None:
                self.client.close()

        app.extensions[self.service_url] = self

    @property
    def service_url_param(self):
        raise NotImplementedError

