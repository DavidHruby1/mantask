# Modules

Domain-level documentation for each business area. Each file covers one coherent product domain from endpoints through to persistence.

- **[tasks.md](tasks.md)** — Task CRUD, the `Task` model with status/priority/effort enums and check constraints, `TaskService` business logic (IN_PROGRESS limits, position tracking, access checks), `Task` repository queries with dynamic filtering, and `Task` API endpoints. Read this when working on task creation, listing, filtering, or status transitions.
- **[auth-and-teams.md](auth-and-teams.md)** — Bootstrap/initialization flow, login/logout/session management, user and user-session persistence, team and team-membership models, and the active-team resolution chain. Read this when working on authentication, session handling, bootstrap secrets, or team structure.

## Gaps

- The `tests/` directory is empty; no test documentation exists.
- No module covers frontend interaction patterns — see the frontend docs for that boundary.
