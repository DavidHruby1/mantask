# Tasks Module

## Summary

This module covers task read/write flows for a team-scoped task table. The main path is: router → service → repository → SQLAlchemy model, with Pydantic schemas enforcing request/response shape. The current DELETE route hard-deletes rows; workflow movement uses a dedicated atomic route.

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

`TaskCreate` normalizes `title` and `layer`, rejects past `review_date`/`due_date`, defaults to `BACKLOG`, and allows creation in `BACKLOG`, `TODO`, or `IN_PROGRESS`. The creator must be a member of the active team, and optional assignee/reviewer members must also belong to that team. Before reading either capacity or the append position, `create_task()` acquires the same transaction-scoped team advisory lock used by movement. An `IN_PROGRESS` payload then calls `_can_create_in_progress_task()`, which counts current `IN_PROGRESS` tasks for the team and compares that count to `get_in_progress_limit()`. New tasks append in their team/status column at `1000` or the last position plus `1000`; creation returns a safe conflict when that append would exceed PostgreSQL `INTEGER`. `started_working_at` is set when a task is created in progress.

### Updating tasks

`TaskUpdate` is partial and does not include `status`; status changes use the move route. The service validates optional assignee/reviewer membership, enforces the `should_review` ↔ reviewer presence rule, and prevents a task already in `REVIEW` from becoming non-reviewable. Together with move validation, this means a `should_review=false` task can neither enter nor remain in `REVIEW`.

### Moving and reordering tasks

`PATCH /tasks/{task_id}/move` accepts `TaskMove` and returns the committed `TaskRead`. The endpoint authenticates through the normal session dependency, reuses `get_accessible_task()` for moved-task access, and owns one commit/rollback boundary around service orchestration. Invalid transitions and missing, cross-team, or wrong-status anchors return `400`; capacity and position exhaustion return `409`. Commit-time integrity collisions also return `409` as a final safety net, not as the expected allocation mechanism. Other database failures return a safe `500`. Clients should refetch before retrying a conflict rather than assuming a partial move was retained.

`TaskService.move_task()` first acquires the team advisory lock and refreshes the moved task, so status, position, and capacity decisions use the state committed while the request waited. A self-anchor then returns the refreshed task as a `200` no-op before transition, capacity, or anchor validation and without staging an ORM mutation. Create and move therefore serialize same-team position allocation and `IN_PROGRESS` capacity while different teams remain independent; the previous concurrent capacity race is closed.

After the self-anchor guard, the service owns transition direction, review eligibility, count-based `IN_PROGRESS` capacity, placement no-ops, sparse-position allocation, lifecycle timestamps, and returned/reopened counters. `list(TaskStatus)` is intentionally the workflow policy: `BACKLOG`, `TODO`, `IN_PROGRESS`, `REVIEW`, `DONE`. Forward moves advance one applicable stage (non-review work advances from `IN_PROGRESS` to `DONE`), while backward moves may cross stages. Same-status requests already adjacent to their requested anchor are intentionally no-ops and do not read `IN_PROGRESS` capacity.

Lifecycle timestamps describe the current pass. `BACKLOG` and `TODO` have no lifecycle timestamps. Every new entry into `IN_PROGRESS` sets a new start time and clears review/completion. Every new entry into `REVIEW` preserves the start, sets a new review time, and clears completion. Entry into `DONE` preserves start and the current review time only when the task passed through review, then sets completion. Returning before review clears the review timestamp, and returning from `DONE` clears completion. A backward move from `REVIEW` increments `returned_count`; a backward move from `DONE` increments `reopened_count`; forward and same-status moves change neither counter, and movement never changes `blocked_count`.

The repository resolves anchors only within the destination team/status while excluding the moved task. Missing, stale, cross-team, and wrong-status anchors share `Anchor is invalid or stale`; self-anchor is handled earlier as a successful no-op. Positions use prepend/midpoint/append gaps where possible. Exhausted space triggers a destination-only rebalance in `(position, id)` order; only `uq_task_team_status_position` is deferred, and only inside that rebalance transaction. The source column is never compacted.

### Deleting tasks

`DELETE /tasks/{task_id}` loads the accessible task and calls `db.delete(task)`. It commits the transaction and converts `IntegrityError` to `ApiConflictError`; other `SQLAlchemyError` failures become `ApiInternalServerError`.

### Data model and enums

`TaskStatus` exposes `BACKLOG`, `TODO`, `IN_PROGRESS`, `REVIEW`, and `DONE`; `BACKLOG` is part of the workflow and declaration order is the fixed authoritative workflow policy. `TaskPriority` is also a string enum. `TaskEffort` is an `IntEnum` persisted with `IntEnumType`, which stores the value as a `SmallInteger` and converts it back to the enum on reads. `Task` defines a deferrable, initially immediate unique constraint on `(team_id, status, position)` and check constraints for positive position, non-blank `layer`/`title`, non-negative counters, completed/submitted-review consistency, and `should_review`/reviewer consistency. Ordinary writes therefore receive immediate uniqueness checks; only a transaction that explicitly defers the named constraint can temporarily overlap positions.

### Ordering migration

The persisted upgrade has two revisions because PostgreSQL 11 requires enum additions outside a transaction. The first adds `backlog` in an Alembic autocommit block. The dependent transactional revision checks integer capacity, changes the database default to `backlog`, and assigns `1000, 2000, ...` within every `(team_id, status)` partition using existing `(position, id)` order before replacing the unique constraint. Existing statuses are not rewritten. The ordering downgrade restores the `todo` default and ordinary immediate uniqueness while retaining sparse positions. The unchanged enum-removal downgrade refuses to proceed while any `BACKLOG` task exists; disposable PostgreSQL 16 validation also exposed a pre-existing cross-enum comparison failure when no backlog rows exist, recorded in `.opencode/artifacts/task-001/RISKS.md`.

### Schemas

`TaskFilters` is the repository shape with a required `team_id`; `TaskQuery` adds an optional `team_id` for request parsing. `TaskFilterFields.normalize_statuses()` collapses an empty list to `None`. `TaskMove` supplies the required destination status and optional predecessor anchor.

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
- Movement has no role-based authorization or assignee-only policy beyond existing active-team membership access.
- The team advisory lock is cooperative: every future task position or `IN_PROGRESS` capacity writer must reuse `lock_task_positions()`.
- Movement does not lock whole columns, compact source gaps, or automatically retry board conflicts.

## Sources

- `app/api/endpoints/tasks.py`: route definitions, commit/rollback flow, and error mapping.
- `app/services/tasks.py`: team resolution, access checks, create/update rules, and limit enforcement.
- `app/repositories/tasks.py`: team advisory locking, filtering, counting, position lookup, insert, and update helpers.
- `app/models/task.py`: table columns, relationships, unique constraint, and check constraints.
- `app/models/enums.py`: enum values and `IntEnumType` behavior.
- `app/schemas/task.py`: request/response/query schemas and field validators.
