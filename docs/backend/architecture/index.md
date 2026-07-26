# Architecture

Cross-cutting technical structure of the backend — how requests flow, how layers are separated, and how the application is wired together.

- **[backend.md](backend.md)** — FastAPI application structure, layered architecture (endpoints → services → repositories → models), dependency injection chain, AppError exception hierarchy, configuration via pydantic-settings, SQLAlchemy database setup, and Alembic migrations. Start here to understand the overall backend shape before diving into modules.

## Gaps

- No deployment, CI, or infrastructure docs — these are outside the current documentation scope.
- No architecture-level auth flow diagram exists yet; see [auth-and-teams.md](../modules/auth-and-teams.md) for auth code documentation.
