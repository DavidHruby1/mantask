# Graph Report - mantask  (2026-07-18)

## Corpus Check
- 70 files · ~9,510 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 409 nodes · 841 edges · 39 communities (36 shown, 3 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 60 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dd9d6fd9`
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

## God Nodes (most connected - your core abstractions)
1. `Task` - 24 edges
2. `TaskCreate` - 23 edges
3. `TaskUpdate` - 20 edges
4. `AppError` - 19 edges
5. `TaskStatus` - 19 edges
6. `TaskService` - 19 edges
7. `BootstrapSetup` - 16 edges
8. `Base` - 15 edges
9. `TaskEffort` - 15 edges
10. `ApiInternalServerError` - 13 edges

## Surprising Connections (you probably didn't know these)
- `upgrade()` --indirect_call--> `TaskEffort`  [INFERRED]
  backend/alembic/versions/83e5ec226cc6_initial_migration.py → backend/app/models/enums.py
- `Task` --uses--> `Base`  [INFERRED]
  backend/app/models/task.py → backend/app/core/db.py
- `TaskService` --uses--> `ApiConflictError`  [INFERRED]
  backend/app/services/tasks.py → backend/app/error.py
- `TaskService` --uses--> `ApiInternalServerError`  [INFERRED]
  backend/app/services/tasks.py → backend/app/error.py
- `TaskRead` --uses--> `TaskStatus`  [INFERRED]
  backend/app/schemas/task.py → backend/app/models/enums.py

## Import Cycles
- None detected.

## Communities (39 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.10
Nodes (39): TaskEffort, TaskPriority, TaskStatus, Task, count_team_tasks_by_status(), find_tasks(), get_last_task_position(), get_task_by_id() (+31 more)

### Community 1 - "Community 1"
Cohesion: 0.17
Nodes (17): bootstrap_setup(), bootstrap_status(), DbSessionDep, Response, AppAlreadyBootstrappedError, InvalidBootstrapSecretError, is_bootstrapped(), BootstrapResult (+9 more)

### Community 2 - "Community 2"
Cohesion: 0.14
Nodes (31): get_current_session(), DbSessionDep, SessionTokenDep, Base, get_db(), Session, AppConfig, TeamType (+23 more)

### Community 3 - "Community 3"
Cohesion: 0.16
Nodes (20): AppError, AuthenticationFailedError, InvalidSessionError, InvalidTaskError, NoActiveTeamSelectedError, NotAuthenticatedError, TaskAccessDeniedError, TaskNotFoundError (+12 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (21): auth_user(), login(), logout(), CurrentSessionDep, DbSessionDep, Response, SessionTokenDep, ApiInternalServerError (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.27
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

### Community 33 - "test_bootstrap.py"
Cohesion: 0.47
Nodes (5): input_data(), mock_dependencies(), test_bootstrap_application_creates_initial_state(), test_bootstrap_application_propagates_repository_failure(), BootstrapSetup

## Knowledge Gaps
- **86 isolated node(s):** `$schema`, `eslint`, `typescript`, `unicorn`, `oxc` (+81 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TaskCreate` connect `Community 0` to `tasks.py`, `Community 3`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `ApiInternalServerError` connect `Community 4` to `Community 0`, `Community 1`, `Community 3`, `tasks.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `BootstrapSetup` connect `Community 1` to `Community 2`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Task` (e.g. with `Base` and `IntEnumType`) actually correct?**
  _`Task` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `TaskCreate` (e.g. with `TaskEffort` and `TaskPriority`) actually correct?**
  _`TaskCreate` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `TaskUpdate` (e.g. with `TaskEffort` and `TaskPriority`) actually correct?**
  _`TaskUpdate` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `TaskStatus` (e.g. with `Task` and `TaskCreate`) actually correct?**
  _`TaskStatus` has 10 INFERRED edges - model-reasoned connections that need verification._