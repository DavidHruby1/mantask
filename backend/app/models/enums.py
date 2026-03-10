from enum import StrEnum, IntEnum


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class UserRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    REVIEWER = "reviewer"
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