from enum import Enum


class StrEnum(str, Enum):
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"'{self.value}'"
