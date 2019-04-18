from typing import List

from flask import g
from werkzeug.local import LocalProxy

from informatics_front.utils.decorators import deprecated


class RequestUser:
    id: int
    roles: List[str]

    def __init__(self, user_dict):
        self.id = user_dict['id']
        self.roles = user_dict['roles']

    def __set__(self, instance, value):
        for k, v in value.items():
            setattr(self, k, v)

    @deprecated('dict replaced by RequestUser')
    def __setitem__(self, key, item):
        self.__dict__[key] = item

    @deprecated('dict replaced by RequestUser')
    def __getitem__(self, key):
        return self.__dict__[key]

    @deprecated('dict replaced by RequestUser')
    def __contains__(self, item):
        return item in self.__dict__


def get_current_user() -> RequestUser:
    return getattr(g, 'user', None)


current_user: RequestUser = LocalProxy(get_current_user)
