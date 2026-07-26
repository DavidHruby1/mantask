# Graph Report - mantask  (2026-07-25)

## Corpus Check
- 79 files · ~22,253 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 491 nodes · 977 edges · 43 communities (41 shown, 2 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 75 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4c7460fc`
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
- Functionality
- Research: Task Move Endpoint
- Constraints & Invariants
- Plan: Atomic Task Movement

## God Nodes (most connected - your core abstractions)
1. `Task` - 24 edges
2. `TaskCreate` - 24 edges
3. `Functionality` - 24 edges
4. `TaskUpdate` - 21 edges
5. `TaskStatus` - 20 edges
6. `TaskService` - 20 edges
7. `AppError` - 19 edges
8. `User` - 18 edges
9. `BootstrapSetup` - 18 edges
10. `Team` - 17 edges

## Surprising Connections (you probably didn't know these)
- `upgrade()` --indirect_call--> `TaskEffort`  [INFERRED]
  backend/alembic/versions/83e5ec226cc6_initial_migration.py → backend/app/models/enums.py
- `Task` --uses--> `Base`  [INFERRED]
  backend/app/models/task.py → backend/app/core/db.py
- `UserSession` --uses--> `Base`  [INFERRED]
  backend/app/models/user_session.py → backend/app/core/db.py
- `TaskService` --uses--> `NoActiveTeamSelectedError`  [INFERRED]
  backend/app/services/tasks.py → backend/app/error.py
- `LoginService` --uses--> `TeamNotFoundError`  [INFERRED]
  backend/app/services/auth.py → backend/app/error.py

## Import Cycles
- None detected.

## Communities (43 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (38): TaskEffort, TaskPriority, TaskStatus, Task, count_team_tasks_by_status(), find_tasks(), get_last_task_position(), get_task_by_id() (+30 more)

### Community 1 - "Community 1"
Cohesion: 0.17
Nodes (15): bootstrap_setup(), bootstrap_status(), DbSessionDep, Response, BootstrapResult, BootstrapSetup, BootstrapStatus, BaseModel (+7 more)

### Community 2 - "Community 2"
Cohesion: 0.20
Nodes (21): Base, AppConfig, TeamType, UserRole, TeamMember, Team, User, create_app_config() (+13 more)

### Community 3 - "Community 3"
Cohesion: 0.19
Nodes (18): ApiConflictError, AppAlreadyBootstrappedError, AppError, InvalidBootstrapSecretError, InvalidTaskError, TaskAccessDeniedError, TaskNotFoundError, TeamInactiveError (+10 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (22): auth_user(), login(), logout(), CurrentSessionDep, DbSessionDep, Response, SessionTokenDep, ApiInternalServerError (+14 more)

### Community 5 - "Community 5"
Cohesion: 0.23
Nodes (16): AuthenticationFailedError, InvalidSessionError, NoActiveTeamSelectedError, UserSession, is_team_member(), create_user(), create_user_session_record(), get_user_by_email() (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (15): render_item(), run_migrations_offline(), run_migrations_online(), upgrade(), get_current_session(), DbSessionDep, SessionTokenDep, get_settings() (+7 more)

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
Cohesion: 0.27
Nodes (13): delete_task(), get_task(), get_tasks(), patch_task(), post_task(), CurrentSessionDep, DbSessionDep, # TODO: Task doesn't have to have assignee, it can be picked up by anyone if nob (+5 more)

### Community 27 - "tsconfig.app.json"
Cohesion: 0.15
Nodes (13): compilerOptions, noUncheckedIndexedAccess, paths, tsBuildInfoFile, exclude, extends, include, @/* (+5 more)

### Community 28 - ".prettierrc.json"
Cohesion: 0.33
Nodes (5): printWidth, $schema, semi, singleQuote, tabWidth

### Community 30 - "Mantask"
Cohesion: 0.50
Nodes (3): @opencode-ai/plugin, dependencies, @opencode-ai/plugin

### Community 39 - "Functionality"
Cohesion: 0.05
Nodes (38): Commands, Progressive Disclosure, Project Purpose, Tech Stack & Dependencies, 1st Version of MVP, 2nd Version of MVP, Account Settings, Adding a Task (+30 more)

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
- **153 isolated node(s):** `@opencode-ai/plugin`, `$schema`, `eslint`, `typescript`, `unicorn` (+148 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TaskCreate` connect `Community 0` to `tasks.py`, `Community 3`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `BootstrapSetup` connect `Community 1` to `Community 2`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `ApiInternalServerError` connect `Community 4` to `Community 0`, `Community 1`, `Community 3`, `tasks.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Task` (e.g. with `Base` and `IntEnumType`) actually correct?**
  _`Task` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `TaskCreate` (e.g. with `TaskEffort` and `TaskPriority`) actually correct?**
  _`TaskCreate` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `TaskUpdate` (e.g. with `TaskEffort` and `TaskPriority`) actually correct?**
  _`TaskUpdate` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `TaskStatus` (e.g. with `Task` and `TaskCreate`) actually correct?**
  _`TaskStatus` has 10 INFERRED edges - model-reasoned connections that need verification._