# Backend Architecture

## Summary

This backend is a FastAPI application centered on a single `/api` router tree, a shared database/session layer, a common `AppError` response path, and Alembic-managed SQLAlchemy migrations.

## Start Here

- `app/main.py`: app assembly, router mounting, CORS, health check, and global error handling.
- `app/core/config.py`: runtime settings source and cached singleton.
- `app/core/db.py`: SQLAlchemy engine, session factory, and FastAPI DB dependency.
- `app/api/dependencies.py`: request-scoped DB and session dependencies.
- `app/error.py`: shared application error types and status codes.
- `alembic/env.py`: migration runner and ORM metadata wiring.
- `alembic/versions/83e5ec226cc6_initial_migration.py`: baseline schema.

## How It Works

### Application assembly

`app/main.py` creates the FastAPI app with `settings.APP_NAME` as the title. It mounts an `APIRouter` with prefix `/api` and includes the `auth`, `bootstrap`, and `tasks` routers beneath it. The same module adds CORS middleware for `http://localhost:5173`, allows credentials, and exposes a `/health` endpoint that returns `{"status": "ok"}`.

### Configuration

`app/core/config.py` defines a `Settings` class backed by `pydantic-settings`. It loads from `.env`, treats environment keys as case-insensitive, and requires `DATABASE_URL`. The documented settings are `APP_NAME`, `DEBUG`, `DATABASE_URL`, `BOOTSTRAP_SECRET`, `SECRET_KEY`, `SESSION_COOKIE_NAME`, `SESSION_EXPIRE_DAYS`, and `DEFAULT_TIMEZONE`. `get_settings()` is wrapped in `lru_cache`, and the module exports a singleton `settings` instance.

### Database session handling

`app/core/db.py` builds the SQLAlchemy engine with `pool_pre_ping=True`, `pool_size=10`, and `max_overflow=20`, and enables SQL echo when `settings.DEBUG` is true. `SessionLocal` is configured with `autoflush=False`, `autocommit=False`, and `expire_on_commit=False`. `get_db()` is the FastAPI dependency generator: it yields a session, then always closes it in `finally`.

Task movement illustrates endpoint-owned transaction completion: the authenticated move endpoint calls the task service, commits once, refreshes the result, and rolls back before translating any database failure. Creation and movement acquire the same transaction-scoped PostgreSQL advisory lock keyed by a fixed repository namespace and `team_id` before capacity or position reads; movement refreshes its previously access-checked task after acquiring the lock and before using mutable status or position. Endpoint commit/rollback releases the lock automatically, and unrelated teams use different lock keys.

The service owns the fixed `TaskStatus` workflow order (including `BACKLOG`), lifecycle re-entry timestamps, capacity, counters, and sparse-position policy; task repositories own the shared lock, scoped neighbor reads, and destination normalization. Self-anchor is a post-lock/post-refresh `200` no-op, and existing-adjacency same-column requests are intentional no-ops. Invalid transitions and anchors are client-input `400` errors, while capacity/position exhaustion and commit collisions are `409`. Ordinary task writes keep position uniqueness immediate. Only destination rebalance executes `SET CONSTRAINTS uq_task_team_status_position DEFERRED`, within the same transaction as status, lifecycle, counters, and final position; positivity and every other constraint remain immediate. A commit-time `IntegrityError` is a safety net rather than an allocation mechanism.

### Request dependencies and current session lookup

`app/api/dependencies.py` defines `DbSessionDep` as `Annotated[Session, Depends(get_db)]`. `SessionTokenDep` reads a cookie using `settings.SESSION_COOKIE_NAME`. `get_current_session()` requires that cookie, passes it to `session_auth_service.get_valid_session_by_token(db, session_token)`, and raises `NotAuthenticatedError` when the cookie is missing. Invalid, expired, or revoked sessions are signaled by `InvalidSessionError` from the auth service. `CurrentSessionDep` is the typed dependency for endpoints that need the authenticated `UserSession`.

### Error handling

`app/error.py` defines `AppError` with `status_code` and `detail`, plus 13 concrete subclasses for authentication, bootstrap, team, task, conflict, and internal server error cases. `app/main.py` registers one exception handler for the whole `AppError` hierarchy and serializes errors as `{"detail": ...}` with the exception's status code.

### Migrations

`alembic/env.py` points Alembic at `settings.DATABASE_URL`, imports model metadata from `Base.metadata`, and defines a custom `render_item()` hook so `IntEnumType` values are rendered correctly during autogeneration. It uses the standard offline and online Alembic runners. The initial migration creates `app_config`, `app_users`, `teams`, `user_sessions`, `team_members`, and `tasks`. The task ordering upgrade is split in two for PostgreSQL 11: an autocommit revision adds `BACKLOG` to the native enum, then a transactional revision changes the creation default and normalizes each team/status column to gaps of `1000` without changing its `(position, id)` visible order. The final `(team_id, status, position)` constraint is deferrable for explicit rebalancing transactions but remains immediate by default for ordinary writes.

## Data Flow

1. A request enters FastAPI and route handlers under `/api` resolve `DbSessionDep` and, when needed, `CurrentSessionDep`.
2. The DB dependency opens a SQLAlchemy session; the cookie dependency reads the configured session token cookie.
3. Session validation hashes the token and looks up the matching `UserSession` row through the auth service; a missing cookie becomes `NotAuthenticatedError`, while an invalid, expired, or revoked session becomes `InvalidSessionError`.
4. Handlers call services and repositories, then commit or roll back their own DB work; any `AppError` is converted to a JSON response by the global handler.

## Key Dependencies

- FastAPI routing, `Depends`, `Cookie`, `JSONResponse`, and `CORSMiddleware`.
- `pydantic-settings` for environment-backed configuration.
- SQLAlchemy engine/session machinery and Alembic context.
- `settings.SESSION_COOKIE_NAME` and `settings.SESSION_EXPIRE_DAYS` for the session-cookie contract.
- `IntEnumType` custom rendering in Alembic.
- ORM metadata imported into `alembic/env.py` so autogeneration sees the model graph.

## Known Risks

- `DATABASE_URL` is required; startup cannot build settings without it.
- `SECRET_KEY` defaults to `change-me-in-production`, so production must override it.
- CORS is restricted to `http://localhost:5173` in the current app setup.
- Auth failure paths are split between `NotAuthenticatedError` for a missing cookie and `InvalidSessionError` for an invalid, expired, or revoked session.
- `SESSION_COOKIE_NAME` is part of the request contract because the dependency reads that cookie name directly.
- Task movement relies on existing membership rather than role-based policy and does not lock whole columns. Count-based `IN_PROGRESS` enforcement is serialized by the shared team advisory lock.
- Advisory-lock correctness is cooperative: future task position and capacity writers must call the repository lock helper before relevant reads.
- Movement conflicts require clients to refetch authoritative board state; the backend does not retry automatically.

## Sources

- `app/main.py`: app/router assembly, CORS, health route, and `AppError` handler.
- `app/core/config.py`: settings fields, `.env` loading, and cached singleton creation.
- `app/core/db.py`: engine/session configuration and DB dependency generator.
- `app/api/dependencies.py`: DB/session dependency chain and cookie lookup.
- `app/error.py`: `AppError` base class and concrete subclasses.
- `alembic/env.py`: Alembic configuration, metadata wiring, and `IntEnumType` rendering.
- `alembic/versions/83e5ec226cc6_initial_migration.py`: initial schema shape.
- `alembic/versions/69b849fd1043_.py`: task unique constraint added after the initial migration.
- `alembic/versions/2d4c6e8f0a1b_add_backlog_task_status.py`: PostgreSQL enum addition and guarded removal.
- `alembic/versions/4f6a8b0c2d3e_normalize_task_positions.py`: sparse normalization, default, and deferrable uniqueness.
- `app/api/endpoints/auth.py`, `app/api/endpoints/bootstrap.py`, `app/api/endpoints/tasks.py`: request flow using the shared dependencies and commit/rollback pattern.
