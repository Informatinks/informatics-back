import enum
import typing

from sqlalchemy import types
from sqlalchemy.engine.interfaces import Dialect

# Unfortunately I have no idea how to test custom
# types. SQLAlchemy doc has no mention about that.
# If you occasionally know how to help it to be tested
# Please text to D. Dubovitskiy.


class IntEnum(types.TypeDecorator):
    """Represents an Enum as integer.

    IMPORTANT: all enum values have to be
    integer values.

    Usage:
        class Status(enum.Enum):
            DRAFT = 1
            ONGOING = 2

        ...

        status = db.Column(IntEnum(Status),
                           nullable=False,
                           default=Status.DRAFT)

    Migrations notice:
        Seems like `alembic` doesn't support custom
        field types. If you add an enum field to the
        model, make sure it has proper configuration.

        Here is an example:

        sa.Column('status', sa.Integer(), nullable=False,
                  server_default=str(CourseStatus.DRAFT.value)),

        `server_default` parameter has to be `str` due to
        alembic restrictions (it normally represented inside
        the database as expected).
    """

    def __init__(self, enum_class: typing.Type[enum.Enum], *args, **kwargs):
        types.TypeDecorator.__init__(self, *args, **kwargs)
        self.enum = enum_class

    impl = types.Integer

    def process_bind_param(self, value: typing.Union[typing.Type[enum.Enum], str], dialect: Dialect):
        if isinstance(value, str):
            return getattr(self.enum, value).value
        return value.value

    def process_result_value(self, value: int, dialect: Dialect):
        enum_members = vars(self.enum)['_value2member_map_']
        return enum_members[value]

    # This is a hack for alembic and defined here to get migrations work
    # as expected. See the link below.
    # https://github.com/zzzeek/alembic/blob/master/alembic/autogenerate/render.py#L594
    __module__ = 'sqlalchemy.types'

    def __repr__(self):
        """Return __repr__ or integer."""
        return repr(self.impl)