# Tasks Module

## Summary

This module covers task read/write flows for a team-scoped task table. The main path is: router → service → repository → SQLAlchemy model, with Pydantic schemas enforcing request/response shape. The current DELETE route hard-deletes rows; there is no soft-delete or move-to-done flow in this source.

## Start Here

- `app/api/endpoints/tasks.py`: HTTP entry points, transaction boundaries, and error translation.
- `app/services/tasks.py`: access checks, team resolution, task creation rules, and write validation.
- `app/models/task.py`: table shape, relationships, and database constraints.
- `app/schemas/task.py`: request/response/query models and field validation.

## How It Works

### Listing tasks

`GET /tasks/` accepts `TaskQuery` as query parameters. `TaskService._resolve_task_filters()` chooses `query.team_id` when present; otherwise it falls back to `session.user.last_active_team_id` and raises `NoActiveTeamSelectedError` if that is missing. It then verifies that the team exists, is active, and that the requester belongs to it. If `assignee_member_id` is provided, the service validates that the member belongs to the same team. The repository then runs `find_tasks()` with the resolved `TaskFilters` and returns tasks ordered by `status`, `position`, and `id`.

### Reading one task

`GET /tasks/{task_id}` uses `get_accessible_task()`. The service loads the row by primary key, raises `TaskNotFoundError` if it is missing, then checks team membership, team existence, and active status before returning the task.

### Creating tasks

`TaskCreate` normalizes `title` and `layer`, rejects past `review_date`/`due_date`, defaults to `BACKLOG`, and allows creation in `BACKLOG`, `TODO`, or `IN_PROGRESS`. In `create_task()`, an `IN_PROGRESS` payload triggers `_can_create_in_progress_task()`, which counts current `IN_PROGRESS` tasks for the team and compares that count to `get_in_progress_limit()`. The creator must be a member of the active team, and optional assignee/reviewer members must also belong to that team. New tasks append in their team/status column at `1000` or the last position plus `1000`; creation returns a safe conflict when that append would exceed PostgreSQL `INTEGER`. `started_working_at` is still set when a task is created in progress.

### Updating tasks

`TaskUpdate` is partial and does not include `status`, so this scope does not implement a status-transition write path. The service validates optional assignee/reviewer membership and enforces the `should_review` ↔ reviewer presence rule before applying the update dictionary to the ORM object.

### Deleting tasks

`DELETE /tasks/{task_id}` loads the accessible task and calls `db.delete(task)`. It commits the transaction and converts `IntegrityError` to `ApiConflictError`; other `SQLAlchemyError` failures become `ApiInternalServerError`.

### Data model and enums

`TaskStatus` exposes `BACKLOG`, `TODO`, `IN_PROGRESS`, `REVIEW`, and `DONE`; `TaskPriority` is also a string enum. `TaskEffort` is an `IntEnum` persisted with `IntEnumType`, which stores the value as a `SmallInteger` and converts it back to the enum on reads. `Task` defines a deferrable, initially immediate unique constraint on `(team_id, status, position)` and check constraints for positive position, non-blank `layer`/`title`, non-negative counters, completed/submitted-review consistency, and `should_review`/reviewer consistency. Ordinary writes therefore receive immediate uniqueness checks; only a transaction that explicitly defers the named constraint can temporarily overlap positions.

### Ordering migration

The persisted upgrade has two revisions because PostgreSQL 11 requires enum additions outside a transaction. The first adds `backlog` in an Alembic autocommit block. The dependent transactional revision checks integer capacity, changes the database default to `backlog`, and assigns `1000, 2000, ...` within every `(team_id, status)` partition using existing `(position, id)` order before replacing the unique constraint. Existing statuses are not rewritten. Downgrade restores the `todo` default and ordinary immediate uniqueness while retaining sparse positions; removal of the enum value refuses to proceed while any `BACKLOG` task exists rather than rewriting it.

### Schemas

`TaskFilters` is the repository shape with a required `team_id`; `TaskQuery` adds an optional `team_id` for request parsing. `TaskFilterFields.normalize_statuses()` collapses an empty list to `None`. `TaskMove` and `TaskDelete` are defined in this module but are not referenced by the routes or service code in this scope.

## Data Flow

1. The router receives a request with a DB session and authenticated session context.
2. The service resolves team scope and validates access or business rules.
3. The repository reads or writes `Task` rows.
4. The endpoint commits, refreshes when needed, and serializes ORM objects to `TaskRead`.

## Key Dependencies

- `get_last_active_team_id()` from `app/services/auth.py`.
- Team access helpers from `app/repositories/teams.py` (`get_team_by_id()`, `get_team_member()`, `get_team_member_by_id()`, `is_team_member()`).
- `get_in_progress_limit()` from `app/repositories/bootstraps.py`.
- `TaskStatus`, `TaskPriority`, `TaskEffort`, and `IntEnumType` from `app/models/enums.py`.
- Error types from `app/error.py` for not-found, access, conflict, and internal-failure cases.

## Known Risks

- The DELETE route is a hard delete, not a soft delete; if soft-delete is intended, the current code does not implement it.
- `TaskUpdate` does not expose `status`, so status transitions are not handled by this route.
- `TaskMove` and `TaskDelete` are currently unused in this scope.
- In-progress limit enforcement only appears in task creation here.

## Sources

- `app/api/endpoints/tasks.py`: route definitions, commit/rollback flow, and error mapping.
- `app/services/tasks.py`: team resolution, access checks, create/update rules, and limit enforcement.
- `app/repositories/tasks.py`: filtering, counting, position lookup, insert, and update helpers.
- `app/models/task.py`: table columns, relationships, unique constraint, and check constraints.
- `app/models/enums.py`: enum values and `IntEnumType` behavior.
- `app/schemas/task.py`: request/response/query schemas and field validators.
