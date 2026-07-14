# Graph Report - .  (2026-07-14)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 250 nodes · 673 edges · 27 communities (25 shown, 2 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 72 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c5e74eb3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 17

## God Nodes (most connected - your core abstractions)
1. `Task` - 23 edges
2. `AppError` - 19 edges
3. `TaskStatus` - 19 edges
4. `TaskService` - 19 edges
5. `User` - 18 edges
6. `Team` - 17 edges
7. `UserSession` - 17 edges
8. `TaskCreate` - 16 edges
9. `TaskEffort` - 15 edges
10. `Base` - 14 edges

## Surprising Connections (you probably didn't know these)
- `upgrade()` --indirect_call--> `TaskEffort`  [INFERRED]
  backend/alembic/versions/83e5ec226cc6_initial_migration.py → backend/app/models/enums.py
- `AppConfig` --uses--> `Base`  [INFERRED]
  backend/app/models/app_config.py → backend/app/core/db.py
- `Task` --uses--> `Base`  [INFERRED]
  backend/app/models/task.py → backend/app/core/db.py
- `UserSession` --uses--> `Base`  [INFERRED]
  backend/app/models/user_session.py → backend/app/core/db.py
- `LoginService` --uses--> `NoActiveTeamSelectedError`  [INFERRED]
  backend/app/services/auth.py → backend/app/error.py

## Import Cycles
- None detected.

## Communities (27 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (29): delete_task(), get_task(), get_tasks(), patch_task(), post_task(), CurrentSessionDep, DbSessionDep, # TODO: Task doesn't have to have assignee, it can be picked up by anyone if nob (+21 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (23): bootstrap_setup(), bootstrap_status(), DbSessionDep, Response, get_settings(), Settings, AppAlreadyBootstrappedError, AppError (+15 more)

### Community 2 - "Community 2"
Cohesion: 0.21
Nodes (20): Base, TeamType, UserRole, TeamMember, Team, User, create_private_team(), create_team() (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.22
Nodes (22): InvalidTaskError, NoActiveTeamSelectedError, TaskAccessDeniedError, TaskNotFoundError, TeamInactiveError, TeamMembershipError, TeamNotFoundError, Task (+14 more)

### Community 4 - "Community 4"
Cohesion: 0.16
Nodes (17): auth_user(), login(), logout(), CurrentSessionDep, DbSessionDep, Response, SessionTokenDep, ApiInternalServerError (+9 more)

### Community 5 - "Community 5"
Cohesion: 0.19
Nodes (14): get_current_session(), DbSessionDep, SessionTokenDep, get_db(), Session, AuthenticationFailedError, InvalidSessionError, NotAuthenticatedError (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (3): upgrade(), IntEnumType, TypeDecorator

### Community 7 - "Community 7"
Cohesion: 0.38
Nodes (4): BaseModel, TeamCreate, TeamRead, TeamUpdate

### Community 8 - "Community 8"
Cohesion: 0.29
Nodes (5): InputProps, inputType, inputVariants, isPasswordVisible, props

### Community 9 - "Community 9"
Cohesion: 0.40
Nodes (5): emit, FormProps, formVariants, handleSubmit(), props

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): ButtonProps, buttonVariants, props

### Community 12 - "Community 12"
Cohesion: 0.50
Nodes (3): attrs, containerVariants, forwardedAttrs

### Community 13 - "Community 13"
Cohesion: 0.50
Nodes (3): HeadingProps, headingVariants, props

### Community 14 - "Community 14"
Cohesion: 0.50
Nodes (3): LinkProps, linkVariants, props

### Community 15 - "Community 15"
Cohesion: 0.50
Nodes (3): props, TextProps, textVariants

## Knowledge Gaps
- **25 isolated node(s):** `ButtonProps`, `props`, `buttonVariants`, `attrs`, `forwardedAttrs` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ApiInternalServerError` connect `Community 4` to `Community 0`, `Community 1`, `Community 3`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `TaskCreate` connect `Community 0` to `Community 3`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `UserSession` connect `Community 5` to `Community 2`, `Community 3`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Task` (e.g. with `Base` and `IntEnumType`) actually correct?**
  _`Task` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `TaskStatus` (e.g. with `Task` and `TaskCreate`) actually correct?**
  _`TaskStatus` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `TaskService` (e.g. with `ApiConflictError` and `ApiInternalServerError`) actually correct?**
  _`TaskService` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `User` (e.g. with `TeamMember` and `Base`) actually correct?**
  _`User` has 4 INFERRED edges - model-reasoned connections that need verification._