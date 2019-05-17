import enum


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
