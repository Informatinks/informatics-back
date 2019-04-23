from marshmallow_enum import EnumField


class ValueEnum(EnumField):
    def __init__(self, enum, *args, **kwargs):
        super().__init__(enum, *args, **kwargs)
        self.by_value = True
