import enum
from enum import Enum


class WorkshopStatus(enum.Enum):
    DRAFT = 1
    ONGOING = 2


class WorkshopVisibility(enum.Enum):
    PUBLIC = 1
    PRIVATE = 2


class WorkshopConnectionStatus(enum.Enum):
    APPLIED = 1  # подана заявка, еще не одобрена
    ACCEPTED = 2  # принят на курс
    DISQUALIFIED = 3  # отчислен с курса (после ACCEPTED)
    REJECTED = 4  # заявка не одобрена (после APPLIED)


class WorkshopMonitorType(enum.Enum):
    """
    Тип монитора:
        IOI - по очкам (количество баллов в задаче)
        ACM - по плюсикам (количество решенных задач)
    """
    IOI = 1
    ACM = 2
    LightACM = 3


class WorkshopMonitorUserVisibility(enum.Enum):
    """ Чьи результаты может видеть ученик, свои или общие"""
    FOR_USER_ONLY = 1
    FULL = 2
    DISABLED_FOR_STUDENT = 3


class ContestProtocolVisibility(Enum):
    FULL = 1
    FIRST_BAD_TEST = 2
    INVISIBLE = 3
