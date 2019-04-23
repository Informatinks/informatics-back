import datetime

from django.db import models


class DateTimeBasedDuration(models.DurationField):
    """ Class for fixing different Duration type understanding:
        - SQLAlchemy uses DATETIME for Duration field
        - DjangoORM uses INTEGER for it.
        It works ONLY if database does not have native type INTERVAL
        (btw it is all databases except PostgreSql and Oracle),
        for more information see help(DurationField).
    """

    @classmethod
    def _from_timestamp(cls, value: datetime.datetime, *__):
        if value is not None:
            return value - datetime.datetime.fromtimestamp(0)

    def get_db_converters(self, connection):
        converters = []
        if not connection.features.has_native_duration_field:
            converters.append(self._from_timestamp)
        return converters

    def get_db_prep_value(self, value: datetime.timedelta, connection, prepared=False):
        if value is None:
            return None
        return datetime.datetime.fromtimestamp(0) + value
