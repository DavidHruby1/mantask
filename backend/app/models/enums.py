from enum import StrEnum, IntEnum

from sqlalchemy import SmallInteger, TypeDecorator


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class UserRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    CONTRACTOR = "contractor"
    GUEST = "guest"


class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskEffort(IntEnum):
    XS = 1
    S = 2
    M = 3
    L = 5
    XL = 8


class IntEnumType(TypeDecorator):
    impl = SmallInteger
    cache_ok = True

    def __init__(self, enum_cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum_cls = enum_cls

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, int):  # IntEnum included
            return int(self.enum_cls(value))  # validate through enum
        raise TypeError(
            f"Expected {self.enum_cls.__name__} or int, got {type(value).__name__}"
        )

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum_cls(value)