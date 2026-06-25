class AppError(Exception):
    status_code = 500
    detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = self.detail if detail is None else detail
        super().__init__(self.detail)


class NotAuthenticatedError(AppError):
    status_code = 401
    detail = "Not authenticated"


class AuthenticationFailedError(AppError):
    status_code = 401
    detail = "Authentication failed"


class NoActiveTeamSelectedError(AppError):
    status_code = 409
    detail = "No active team selected"


class TeamNotFoundError(AppError):
    status_code = 404
    detail = "Team not found"


class TeamInactiveError(AppError):
    status_code = 409
    detail = "Team is inactive"


class TaskNotFoundError(AppError):
    status_code = 404
    detail = "Task not found"


class TaskAccessDeniedError(AppError):
    status_code = 403
    detail = "You cannot view this task"


class TeamMembershipError(AppError):
    status_code = 409
    detail = "You are not a member of this team"


class InvalidTaskError(AppError):
    status_code = 400
    detail = "Invalid payload"


class AppAlreadyBootstrappedError(AppError):
    status_code = 409
    detail = "App already bootstrapped"


class InvalidBootstrapSecretError(AppError):
    status_code = 403
    detail = "Invalid bootstrap"


class InvalidSessionError(AppError):
    status_code = 403
    detail = "Invalid session"


class ApiConflictError(AppError):
    status_code = 409
    detail = "Conflict"


class ApiInternalServerError(AppError):
    status_code = 500
    detail = "Internal server error"
