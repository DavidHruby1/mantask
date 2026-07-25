# Graph Report - mantask  (2026-07-21)

## Corpus Check
- 78 files · ~22,080 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 489 nodes · 913 edges · 44 communities (40 shown, 4 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 60 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2490f162`
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
- tasks.py
- tsconfig.app.json
- .prettierrc.json
- tsconfig.json
- Mantask
- test_auth.py
- test_bootstrap.py
- Functionality
- Research: Task Move Endpoint
- Constraints & Invariants
- Plan: Atomic Task Movement

## God Nodes (most connected - your core abstractions)
1. `Functionality` - 24 edges
2. `Task` - 24 edges
3. `TaskCreate` - 23 edges
4. `TaskUpdate` - 20 edges
5. `AppError` - 19 edges
6. `TaskStatus` - 19 edges
7. `TaskService` - 19 edges
8. `BootstrapSetup` - 16 edges
9. `Base` - 15 edges
10. `TaskEffort` - 15 edges

## Surprising Connections (you probably didn't know these)
- `upgrade()` --indirect_call--> `TaskEffort`  [INFERRED]
  backend/alembic/versions/83e5ec226cc6_initial_migration.py → backend/app/models/enums.py
- `AppConfig` --uses--> `Base`  [INFERRED]
  backend/app/models/app_config.py → backend/app/core/db.py
- `Task` --uses--> `Base`  [INFERRED]
  backend/app/models/task.py → backend/app/core/db.py
- `TaskService` --uses--> `ApiConflictError`  [INFERRED]
  backend/app/services/tasks.py → backend/app/error.py
- `TaskService` --uses--> `ApiInternalServerError`  [INFERRED]
  backend/app/services/tasks.py → backend/app/error.py

## Import Cycles
- None detected.

## Communities (44 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (39): TaskEffort, TaskPriority, TaskStatus, Task, count_team_tasks_by_status(), find_tasks(), get_last_task_position(), get_task_by_id() (+31 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (19): bootstrap_setup(), bootstrap_status(), DbSessionDep, Response, AppConfig, create_app_config(), get_in_progress_limit(), is_bootstrapped() (+11 more)

### Community 2 - "Community 2"
Cohesion: 0.16
Nodes (27): get_current_session(), DbSessionDep, SessionTokenDep, Base, get_db(), Session, TeamType, UserRole (+19 more)

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (22): AppAlreadyBootstrappedError, AppError, AuthenticationFailedError, InvalidBootstrapSecretError, InvalidSessionError, InvalidTaskError, NoActiveTeamSelectedError, NotAuthenticatedError (+14 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (21): auth_user(), login(), logout(), CurrentSessionDep, DbSessionDep, Response, SessionTokenDep, ApiInternalServerError (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.28
Nodes (8): ensure_active_team_id(), get_last_active_team_id(), hash_session_token(), LoginService, SessionAuthService, Session, User, UserSession

### Community 6 - "Community 6"
Cohesion: 0.17
Nodes (9): render_item(), run_migrations_offline(), run_migrations_online(), upgrade(), get_settings(), Settings, IntEnumType, BaseSettings (+1 more)

### Community 7 - "Community 7"
Cohesion: 0.27
Nodes (5): BaseModel, TeamCreate, TeamRead, TeamUpdate, test_team_update_accepts_explicit_null_name()

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (22): categories, correctness, env, browser, plugins, $schema, attrs, containerVariants (+14 more)

### Community 9 - "Community 9"
Cohesion: 0.40
Nodes (5): emit, FormProps, formVariants, handleSubmit(), props

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (35): eslint, eslint-config-prettier, eslint-plugin-oxlint, eslint-plugin-vue, devDependencies, eslint, eslint-config-prettier, eslint-plugin-oxlint (+27 more)

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): ButtonProps, buttonVariants, props

### Community 12 - "Community 12"
Cohesion: 0.06
Nodes (33): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, pinia, tailwind-merge, tailwindcss (+25 more)

### Community 13 - "Community 13"
Cohesion: 0.50
Nodes (3): HeadingProps, headingVariants, props

### Community 14 - "Community 14"
Cohesion: 0.50
Nodes (3): LinkProps, linkVariants, props

### Community 15 - "Community 15"
Cohesion: 0.50
Nodes (3): props, TextProps, textVariants

### Community 17 - "tasks.py"
Cohesion: 0.28
Nodes (14): delete_task(), get_task(), get_tasks(), patch_task(), post_task(), CurrentSessionDep, DbSessionDep, # TODO: Task doesn't have to have assignee, it can be picked up by anyone if nob (+6 more)

### Community 27 - "tsconfig.app.json"
Cohesion: 0.15
Nodes (13): compilerOptions, noUncheckedIndexedAccess, paths, tsBuildInfoFile, exclude, extends, include, @/* (+5 more)

### Community 28 - ".prettierrc.json"
Cohesion: 0.33
Nodes (5): printWidth, $schema, semi, singleQuote, tabWidth

### Community 39 - "Functionality"
Cohesion: 0.05
Nodes (36): Commands, Progressive Disclosure, Project Purpose, Tech Stack & Dependencies, 1st Version of MVP, 2nd Version of MVP, Account Settings, Adding a Task (+28 more)

### Community 40 - "Research: Task Move Endpoint"
Cohesion: 0.11
Nodes (17): Basis, Boundaries And Flow, Code Map, Conflicts And Unknowns, Constraints And Invariants, Current System, Existing Patterns And Decisions, External Findings (+9 more)

### Community 41 - "Constraints & Invariants"
Cohesion: 0.12
Nodes (16): Acceptance Criteria, Authorization, Constraints & Invariants, Counters, Desired Outcome, Domain Terms, IN_PROGRESS Limit, No-op Behavior (+8 more)

### Community 42 - "Plan: Atomic Task Movement"
Cohesion: 0.25
Nodes (7): Approved Solution, Inputs, Plan: Atomic Task Movement, Plan-Wide Safety, PR 1: Atomic Task Movement, Pull Requests, Residual Risks

## Knowledge Gaps
- **151 isolated node(s):** `Problem`, `Desired Outcome`, `Domain Terms`, `Scope`, `Position Rules` (+146 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TaskCreate` connect `Community 0` to `tasks.py`, `Community 3`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `ApiInternalServerError` connect `Community 4` to `Community 0`, `Community 1`, `Community 3`, `tasks.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `BootstrapSetup` connect `Community 1` to `Community 2`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Task` (e.g. with `Base` and `IntEnumType`) actually correct?**
  _`Task` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `TaskCreate` (e.g. with `TaskEffort` and `TaskPriority`) actually correct?**
  _`TaskCreate` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `TaskUpdate` (e.g. with `TaskEffort` and `TaskPriority`) actually correct?**
  _`TaskUpdate` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Problem`, `Desired Outcome`, `Domain Terms` to the rest of the system?**
  _155 weakly-connected nodes found - possible documentation gaps or missing edges._