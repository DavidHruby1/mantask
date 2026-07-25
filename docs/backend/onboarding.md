# Onboarding

A maintainer's starting path through the backend documentation.

## Recommended Reading Order

1. **[architecture/backend.md](architecture/backend.md)** — Understand the application structure: how FastAPI wires routes, how the three-layer pattern (endpoints → services → repositories → models) works, how dependency injection flows through the request lifecycle, how errors are mapped to HTTP responses, and how the database and migrations are set up.

2. **[modules/auth-and-teams.md](modules/auth-and-teams.md)** — Learn how authentication works from both ends: the one-time bootstrap flow that creates the first user, teams, and config, and the ongoing login/logout/session lifecycle with hashed tokens and cookie-based transport. This also covers the user, team, and team-member data models that everything else depends on.

3. **[modules/tasks.md](modules/tasks.md)** — Learn the task management domain: the `Task` model with its constraints and enum lifecycle, the `TaskService` business rules (IN_PROGRESS limits, sparse position ordering, access checks), and the `Task` repository query patterns.

## Source Layout Reference

```
app/
    main.py              — Application entrypoint, router assembly, error handler
    core/
        config.py        — Settings via pydantic-settings (env vars, .env file)
        db.py            — SQLAlchemy engine, session factory, declarative base
    api/
        dependencies.py  — FastAPI dependency chain (DB session, session auth)
        endpoints/
            auth.py      — POST /auth/login, GET /auth/me, POST /auth/logout
            bootstrap.py — GET /bootstrap/status, POST /bootstrap/setup
            tasks.py     — GET/POST/PATCH/DELETE /tasks/
    services/
        auth.py          — LoginService, SessionAuthService, active-team resolution
        bootstrap.py     — bootstrap_application() one-time setup
        tasks.py         — TaskService business logic
    repositories/
        users.py         — User and user-session data access
        teams.py         — Team and team-member data access
        bootstraps.py    — AppConfig data access
        tasks.py         — Task data access (queries, inserts, updates)
    models/
        task.py          — Task ORM model with 8 check constraints
        user.py          — User ORM model
        user_session.py  — UserSession ORM model
        team.py          — Team ORM model
        team_member.py   — TeamMember ORM model
        app_config.py    — AppConfig singleton ORM model
        enums.py         — TaskStatus, TaskPriority, TaskEffort, UserRole, TeamType
    schemas/
        auth.py          — LoginInput, LoginResult
        bootstrap.py     — BootstrapSetup, BootstrapResult, BootstrapStatus
        task.py          — TaskCreate, TaskUpdate, TaskRead, TaskQuery, TaskFilters
        team.py          — TeamCreate
    error.py             — AppError exception hierarchy (14 error types)
alembic/
    env.py               — Migration runner configuration
    versions/            — Migration scripts, including the two-step BACKLOG/ordering upgrade
```

## Gaps

- No test documentation or test coverage exists yet (tests/ directory is empty).
- No API-first OpenAPI/Swagger documentation strategy is defined beyond what FastAPI auto-generates.
- No frontend-backend contract documentation exists yet.
