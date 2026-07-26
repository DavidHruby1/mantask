# Plan: Atomic Task Movement Corrections

## Approved Solution

Apply the final correction scope in place without changing the existing movement
architecture. Add one repository-owned transaction advisory lock, call it from
creation and movement, refresh moved state after lock acquisition, and retain the
current endpoint transaction boundary, sparse ordering, rebalance, and placement
no-op behavior.

## Implementation

1. Add `lock_task_positions(db, team_id)` with a fixed module namespace and
   `pg_advisory_xact_lock(namespace, team_id)`; it does not commit.
2. In `create_task()`, acquire the lock before `_can_create_in_progress_task()`
   and `get_last_task_position()`.
3. In `move_task()`, lock `task.team_id`, refresh the task, and then handle
   self-anchor before transition, capacity, or anchor validation.
4. Restore `_can_create_in_progress_task` and use it for creation and net entry
   into `IN_PROGRESS`.
5. Map invalid transition/review/anchor input to `InvalidTaskError`, retaining
   `ApiConflictError` for capacity and position exhaustion.
6. Apply the approved lifecycle re-entry matrix and preserve existing backward
   `returned_count` and `reopened_count` events.
7. Add service, HTTP, and real PostgreSQL coverage identified in `GHERKIN.md`.
8. Update backend documentation, these task artifacts, and PR #19's body.
9. Run the complete backend suite, disposable PostgreSQL concurrency and
   migration checks, inspect the diff, then commit and push the PR branch.

## Validation

- Service scenarios `SVC-001` through `SVC-011`.
- PostgreSQL scenarios `PG-001` through `PG-006`.
- Endpoint scenarios `API-001` through `API-009`.
- `python3 -m compileall backend/app backend/alembic`.
- Full `pytest` suite against a disposable migrated PostgreSQL database.

## Non-Goals

No database migration, transaction wrapper, retry mechanism, source compaction,
column-locking redesign, new ordering policy, or unrelated CRUD refactor.
