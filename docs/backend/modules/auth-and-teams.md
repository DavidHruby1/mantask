# Auth and Teams

## Summary

This module owns bootstrap, login/logout, current-session lookup, and the core user/team persistence used by those flows. The main thing to understand is that auth state is stored as a hashed session token, while the active team is derived from the user record and validated against team membership.

## Start Here

- `app/api/endpoints/bootstrap.py`: bootstrap entrypoints and bootstrap-time session creation.
- `app/api/endpoints/auth.py`: login, current-user, and logout request flow.
- `app/services/auth.py`: password verification, session token handling, and active-team selection.

## How It Works

### Bootstrap flow

`POST /bootstrap/setup` first checks `is_bootstrapped(db)`. If an app config row already exists, it rejects the request. It then compares the submitted bootstrap secret with `settings.BOOTSTRAP_SECRET` using `secrets.compare_digest` and rejects missing or mismatched secrets.

When allowed, `bootstrap_application()` creates the singleton `AppConfig`, creates the first `User` with an argon2 password hash, creates a private team and a shared team, and adds `TeamMember` rows for both with `UserRole.OWNER`. It sets `user.last_active_team_id` to the private team before returning the user.

The endpoint then creates a session, commits, sets the session cookie, and returns `BootstrapResult` with `bootstrapped=True` and the user’s active team id. The response body does not include the raw session token.

### Login and logout

`POST /auth/login` authenticates by email and password. `LoginService.authenticate_user()` loads the user by email, uses a dummy argon2 hash when the user is missing, and rejects inactive accounts or password mismatches with `AuthenticationFailedError`.

On success, `LoginService.create_session()` generates a URL-safe token with `secrets.token_urlsafe(32)`, stores only its SHA-256 hex digest, and sets an expiry based on `settings.SESSION_EXPIRE_DAYS`. The endpoint also resolves the active team, commits, and sends the raw token back in both the response body and an `HttpOnly`, `SameSite=lax` cookie.

`POST /auth/logout` reads the session token from the cookie, revokes the matching session by setting `revoked_at` when it exists, commits if anything changed, and deletes the cookie either way.

### Current session lookup

`GET /auth/me` depends on the current session cookie. The dependency path validates the cookie, loads the session by token hash, and rejects missing or invalid sessions. The endpoint then re-runs active-team resolution for the session user and returns `LoginResult(authenticated=True, active_team_id=...)`.

### Active team resolution

`ensure_active_team_id()` first checks `user.last_active_team_id`. If that team exists, is active, and the user is a member, it keeps that id and writes it back to the user when needed. If that lookup fails with `NoActiveTeamSelectedError`, it falls back to the user’s private team via `get_private_team_id()`.

`get_last_active_team_id()` raises `TeamNotFoundError` when `last_active_team_id` is unset. That exception is not caught by `ensure_active_team_id()`, so the fallback path only runs after `NoActiveTeamSelectedError`.

### Persistence model

`User` rows live in `app_users`. The table enforces nonblank username, normalized username, email, and password hash values, with unique constraints on `username_normalized` and `email`. It also tracks `is_active`, timestamps, `profile_picture_path`, and `last_active_team_id`, and it exposes `team_members` and `sessions` relationships.

`UserSession` rows live in `user_sessions`. Each row stores only the SHA-256 hash of the raw session token, plus `created_at`, `expires_at`, `revoked_at`, and the owning `user_id`.

`Team` rows live in `teams`. `TeamType` is a string enum with `private` and `team`. The table enforces that private teams must have `private_owner_user_id` set and shared teams must not, and it keeps a uniqueness rule on `private_owner_user_id`. Teams are active by default and expose `members` and `tasks` relationships.

`TeamMember` rows live in `team_members`. Each row links one user to one team, keeps a `UserRole` value (`owner`, `admin`, `member`, `contractor`, or `guest`), and enforces uniqueness on `(team_id, user_id)`. The model also exposes reverse relationships to the team, user, and task-assignment roles.

`AppConfig` is a singleton table with `id = 1`, `organization_name`, `initialized_at`, and `in_progress_limit`.

## Data Flow

1. A bootstrap request validates the secret, creates `AppConfig`, `User`, `Team`, `TeamMember`, and the first session.
2. A login request verifies credentials, creates a hashed session record, resolves the active team, and sets the session cookie.
3. A session-backed request reads the cookie, validates the stored session, and uses the user record to determine the active team.
4. Logout revokes the stored session hash and clears the cookie.

## Key Dependencies

- `app/api/dependencies.py`: resolves the session cookie and current session object.
- `app/core/config.py`: supplies the cookie name, expiry length, debug flag, and bootstrap secret.
- `app/repositories/users.py`: creates users and session records, and looks up users/sessions by email or token hash.
- `app/repositories/teams.py`: creates teams and memberships, and checks private-team and membership state.
- `app/repositories/bootstraps.py`: checks whether bootstrap already happened and reads `AppConfig` data.
- `app/models/enums.py`: defines `UserRole` and `TeamType`.
- `app/models/user.py`, `app/models/user_session.py`, `app/models/team.py`, `app/models/team_member.py`, `app/models/app_config.py`: persistence for the auth/bootstrap flow.

## Known Risks

- `ensure_active_team_id()` does not catch `TeamNotFoundError`, so a user with no `last_active_team_id` does not reach the private-team fallback.
- `app/models/team.py` uses `List` in relationship annotations without importing it, which is fragile in a non-postponed annotation context.
- `bootstrap_setup()` creates the session cookie only after a successful commit; any database failure returns an internal error instead of a partial bootstrap.

## Sources

- `app/api/endpoints/auth.py`: login, current-user, and logout endpoint behavior.
- `app/api/endpoints/bootstrap.py`: bootstrap status and setup behavior.
- `app/api/dependencies.py`: session-cookie dependency and current-session lookup.
- `app/services/auth.py`: password verification, session creation/revocation, and active-team selection.
- `app/services/bootstrap.py`: bootstrap object creation workflow.
- `app/models/user.py`: user table, constraints, and relationships.
- `app/models/user_session.py`: session table and revocation fields.
- `app/models/team.py`: team table, enum usage, and ownership constraint.
- `app/models/team_member.py`: team membership table and role enum.
- `app/models/app_config.py`: singleton bootstrap config table.
- `app/models/enums.py`: `UserRole` and `TeamType` values.
- `app/repositories/users.py`: user and session persistence helpers.
- `app/repositories/teams.py`: team and membership persistence helpers.
- `app/repositories/bootstraps.py`: bootstrap state helpers.
- `app/schemas/auth.py`: login request/response shapes.
- `app/schemas/bootstrap.py`: bootstrap request/response/status shapes.
- `app/schemas/team.py`: team request/read shapes.
