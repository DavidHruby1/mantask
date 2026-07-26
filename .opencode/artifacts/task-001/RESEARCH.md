# Research: Task Move Endpoint

## Basis

- Brief: `.opencode/artifacts/task-001/BRIEF.md`
- Repository impact: broad
- External evidence: required
- Routing rationale: the HTTP and domain changes remain inside the task module, but safe position allocation changes the task constraint migration, transaction behavior, concurrency control, and test infrastructure. SQLAlchemy flush recovery and PostgreSQL constraint and locking semantics are version-specific external runtime contracts that the repository cannot establish.

## Questions Investigated

- Which task boundaries, constraints, and transaction owners govern creation and movement?
- How must target-column queries treat the task being moved?
- Which transition, timestamp, limit, no-op, and authorization rules must remain true?
- What happens to a SQLAlchemy 2.0 session after a failed flush?
- When does PostgreSQL check UNIQUE and CHECK constraints?
- Which database mechanisms can serialize position allocation and permit safe renumbering?
- What automated validation infrastructure exists?

## Code Map

### Start Here

- `backend/app/api/endpoints/tasks.py:16-105`: task routes, access checks, and commit/rollback ownership.
- `backend/app/services/tasks.py:39-202`: task business rules, position creation, and IN_PROGRESS limit enforcement.
- `backend/app/repositories/tasks.py:11-74`: ordered task queries and persistence helpers.
- `backend/app/models/task.py:28-143`: task columns and database constraints.
- `backend/app/schemas/task.py:112-147`: existing `TaskMove` request and `TaskRead` response.
- `backend/app/core/db.py:13-34`: SQLAlchemy engine and per-request session configuration.
- `backend/alembic/versions/69b849fd1043_.py:24`: existing position uniqueness migration.

### Boundaries And Flow

The endpoint owns commit and rollback. `TaskService` owns business validation and coordinates repository calls. Repository functions execute queries or mutate ORM objects without committing. The per-request `Session` has `autoflush=False`, `autocommit=False`, and `expire_on_commit=False`.

Task creation currently checks the IN_PROGRESS limit, validates members, reads the last position in the requested status, creates the ORM object, and leaves commit to the endpoint. Task updates follow the same endpoint-owned transaction boundary.

### Validation Surface

- `backend/tests/`: empty; no fixtures or tests exist.
- `backend/requirements.txt`: no test runner or HTTP test dependency is declared.
- Alembic upgrade/downgrade against disposable PostgreSQL: can prove migration reversibility and constraint shape.
- PostgreSQL-backed concurrent sessions are needed to validate advisory-lock and constraint behavior, whether exercised manually or by a later testing workflow.

## Current System

`TaskMove` already contains `target_status: TaskStatus` and nullable `anchor_task_id`; no schema fields are missing (`backend/app/schemas/task.py:112-114`). `TaskStatus` is a string enum with `todo`, `in_progress`, `review`, and `done` (`backend/app/models/enums.py:6-10`).

Task creation assigns positions `1, 2, 3, ...` by reading the maximum position and adding one (`backend/app/services/tasks.py:77-86`). The read and insert are not serialized, so concurrent creates can select the same next position. The database ultimately protects `(team_id, status, position)` with `uq_task_team_status_position` (`backend/app/models/task.py:32`).

The `position` column is a PostgreSQL integer with `CHECK (position >= 1)` and no application-level upper bound (`backend/app/models/task.py:33,96`). The unique constraint is currently non-deferrable because neither the model nor its migration declares `DEFERRABLE` (`backend/app/models/task.py:32`, `backend/alembic/versions/69b849fd1043_.py:24`).

Existing repository queries order tasks by status, position, and id. A same-status move must calculate the target column as though the moved task were absent. Otherwise the moved task can be selected as the first task or as the task after the anchor, and a one-task column cannot be recognized as empty (`backend/app/repositories/tasks.py:11-20`).

`_can_create_in_progress_task()` already owns the IN_PROGRESS count and configured limit check and returns whether another task may enter that status (`backend/app/services/tasks.py:185-199`). It can be reused without renaming. The check is currently not serialized with creation.

`get_accessible_task()` validates task existence, team membership, team existence, and team activity (`backend/app/services/tasks.py:134-149`). Existing single-task endpoints call it before service mutation (`backend/app/api/endpoints/tasks.py:64-85,88-105`).

Timestamp constraints require `completed_at` exactly for DONE and allow `submitted_for_review_at` only in REVIEW or DONE (`backend/app/models/task.py:39-47`). `started_working_at` has no corresponding database check (`backend/app/models/task.py:112`). Consequently, backward transitions to TODO or IN_PROGRESS must clear stale review timestamps even when the source status is DONE.

## Constraints And Invariants

- The final committed state must keep position unique within `(team_id, status)` and at least 1.
- Position allocation and IN_PROGRESS net-increase checks must be serialized with competing creates and moves for the same team if their decisions depend on current rows.
- A task loaded for access control before the advisory lock must be refreshed under the lock before status, position, timestamp, or capacity decisions use it.
- Target-column neighbor queries and rebalance input must exclude the moved task.
- `REVIEW -> IN_PROGRESS` is an allowed backward transition. Only invalid forward transitions are rejected.
- Same-status moves do not change timestamps or consume IN_PROGRESS capacity.
- No-op moves perform no ORM mutation or database write.
- The endpoint transaction remains owned by the endpoint; repositories and services do not commit.
- The existing counters and `TaskMove` shape remain unchanged.

## Existing Patterns And Decisions

- Repositories are plain functions receiving `Session`; new position and lock operations belong in `backend/app/repositories/tasks.py`.
- Business rules belong in the singleton `TaskService`; the route should remain thin.
- Endpoints translate commit-time `IntegrityError` into `ApiConflictError` after rollback.
- Alembic is the repository's owner for database constraint changes.
- No existing automated test pattern can be reused. Test design and infrastructure belong to the later testing workflow, not this implementation research artifact.

## Failure And Operational Paths

- A failed ordinary `Session.flush()` invalidates the SQLAlchemy session transaction. Further SQL raises `PendingRollbackError` until an explicit rollback; the service cannot catch `IntegrityError` and continue in the same outer transaction.
- `Session.begin_nested()` creates an explicit savepoint, but first flushes all pending state unconditionally. Dirty collision-prone state must not exist before entering it.
- PostgreSQL CHECK constraints and non-deferrable uniqueness constraints are checked immediately. A failed `position >= 1` check and a failed position unique check are both `IntegrityError` paths but represent different defects.
- Directly renumbering `1000, 1001, 2000` to `1000, 2000, 3000` can transiently violate a non-deferrable unique constraint before the row currently at 2000 moves.
- Under READ COMMITTED, competing writers for the same unique key do not both safely pass and defer the conflict to commit; one can wait and then fail during its statement.
- Transaction-scoped advisory locks are cooperative. Every create or move path that allocates a task position must acquire the same logical lock, and lock ordering must be consistent.
- A deferrable unique constraint can be deferred for the transaction so intermediate renumbering may temporarily duplicate values, while final uniqueness is checked before commit. CHECK constraints remain immediate.

## External Findings

- SQLAlchemy 2.0 requires `Session.rollback()` after an ordinary flush failure before the session can be reused. Explicit savepoints use `Session.begin_nested()`, which unconditionally flushes pending state before establishing the savepoint. These contracts apply to the repository's SQLAlchemy 2.0.49.
- PostgreSQL checks CHECK constraints and non-deferrable UNIQUE constraints immediately when rows are modified. Only UNIQUE, PRIMARY KEY, EXCLUDE, and foreign-key constraints can be deferrable; CHECK cannot.
- `DEFERRABLE INITIALLY IMMEDIATE` preserves immediate checking by default and permits a transaction to run `SET CONSTRAINTS <name> DEFERRED` when a coherent multi-row renumber requires temporary duplicates.
- `pg_advisory_xact_lock(int, int)` holds a cooperative exclusive lock until transaction end. A stable namespace plus `team_id` can serialize all task-position allocation for one team, including empty columns, without lock cleanup code.
- PostgreSQL server version is not pinned in the repository. The cited constraint and advisory-lock capabilities are longstanding PostgreSQL features, but migration and integration tests must run against the deployed major version.

## Planning Constraints

- The plan must not recover from a failed ordinary flush inside the same transaction.
- It must define one lock key used by both task creation and movement before reading limits or positions.
- It must refresh the moved task after acquiring that lock so move decisions do not use pre-lock ORM state.
- It must make intermediate rebalance updates legal under PostgreSQL uniqueness semantics and preserve final uniqueness at commit.
- It must define neighbor and rebalance queries that exclude the moved task.
- It must distinguish expected gap exhaustion from unrelated database constraint failures rather than using generic `IntegrityError` as normal control flow.
- Transaction and constraint paths require validation against PostgreSQL; the later testing workflow owns the concrete automated test design.

## Conflicts And Unknowns

- No blocking conflict remains in the brief. `REVIEW -> IN_PROGRESS` is explicitly authoritative and the contradictory acceptance-criterion example was corrected.
- The deployed PostgreSQL major version is not recorded. This is non-blocking because the required features predate currently supported versions; verify it in the test and deployment environment before migration rollout.

## Sources

### Repository Sources

- `backend/app/core/db.py:13-34`: engine, session options, and request lifetime.
- `backend/app/models/enums.py:6-10`: task statuses.
- `backend/app/models/task.py:28-53,78-96,112-114`: uniqueness, checks, status storage, position type, and timestamps.
- `backend/app/schemas/task.py:112-147`: move request and task response.
- `backend/app/repositories/tasks.py:11-74`: current query and mutation patterns.
- `backend/app/services/tasks.py:49-99,134-149,185-199`: task creation, access checks, and IN_PROGRESS limit.
- `backend/app/api/endpoints/tasks.py:40-105`: endpoint transaction ownership and error translation.
- `backend/alembic/versions/69b849fd1043_.py:24`: current unique constraint migration.
- `backend/requirements.txt:1-8`: SQLAlchemy 2.0.49, psycopg 3.3.4, and absent test dependencies.

### External Sources

- `https://docs.sqlalchemy.org/en/20/faq/sessions.html`: SQLAlchemy 2.0 session state after failed flush and required rollback.
- `https://docs.sqlalchemy.org/en/20/orm/session_transaction.html`: SQLAlchemy 2.0 savepoint lifecycle and unconditional pre-flush of `begin_nested()`.
- `https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.begin_nested`: SQLAlchemy 2.0 nested transaction API.
- `https://www.postgresql.org/docs/current/sql-set-constraints.html`: immediate and deferred constraint semantics, including non-deferrable UNIQUE and CHECK behavior.
- `https://www.postgresql.org/docs/current/sql-createtable.html`: `DEFERRABLE` support and constraint declaration semantics.
- `https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS`: transaction-scoped advisory-lock behavior and caveats.
- `https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS`: two-integer `pg_advisory_xact_lock` contract.
- `https://www.postgresql.org/docs/current/transaction-iso.html`: READ COMMITTED behavior for competing row updates.
