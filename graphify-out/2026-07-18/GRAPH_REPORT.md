# Graph Report - mantask  (2026-07-14)

## Corpus Check
- 68 files · ~9,224 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 399 nodes · 858 edges · 37 communities (35 shown, 2 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 75 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `574b4ee5`
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
- tsconfig.app.json
- .prettierrc.json
- tsconfig.json
- Mantask

## God Nodes (most connected - your core abstractions)
1. `Task` - 24 edges
2. `TaskCreate` - 23 edges
3. `TaskUpdate` - 20 edges
4. `AppError` - 19 edges
5. `TaskStatus` - 19 edges
6. `TaskService` - 19 edges
7. `User` - 18 edges
8. `Team` - 17 edges
9. `UserSession` - 17 edges
10. `BootstrapSetup` - 16 edges

## Surprising Connections (you probably didn't know these)
- `upgrade()` --indirect_call--> `TaskEffort`  [INFERRED]
  backend/alembic/versions/83e5ec226cc6_initial_migration.py → backend/app/models/enums.py
- `Task` --uses--> `Base`  [INFERRED]
  backend/app/models/task.py → backend/app/core/db.py
- `UserSession` --uses--> `Base`  [INFERRED]
  backend/app/models/user_session.py → backend/app/core/db.py
- `User` --uses--> `Base`  [INFERRED]
  backend/app/models/user.py → backend/app/core/db.py
- `LoginService` --uses--> `NoActiveTeamSelectedError`  [INFERRED]
  backend/app/services/auth.py → backend/app/error.py

## Import Cycles
- None detected.

## Communities (37 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.08
Nodes (43): delete_task(), get_task(), get_tasks(), patch_task(), post_task(), CurrentSessionDep, DbSessionDep, # TODO: Task doesn't have to have assignee, it can be picked up by anyone if nob (+35 more)

### Community 1 - "Community 1"
Cohesion: 0.18
Nodes (12): bootstrap_status(), DbSessionDep, BootstrapResult, BootstrapSetup, BootstrapStatus, BaseModel, test_bootstrap_accepts_valid_password(), test_bootstrap_rejects_invalid_organization_or_team_name() (+4 more)

### Community 2 - "Community 2"
Cohesion: 0.21
Nodes (20): Base, AppConfig, TeamType, UserRole, TeamMember, Team, create_app_config(), get_in_progress_limit() (+12 more)

### Community 3 - "Community 3"
Cohesion: 0.15
Nodes (30): bootstrap_setup(), Response, ApiConflictError, ApiInternalServerError, AppAlreadyBootstrappedError, AppError, InvalidBootstrapSecretError, InvalidTaskError (+22 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (20): auth_user(), login(), logout(), CurrentSessionDep, DbSessionDep, Response, SessionTokenDep, ChangePasswordResult (+12 more)

### Community 5 - "Community 5"
Cohesion: 0.16
Nodes (23): get_current_session(), DbSessionDep, SessionTokenDep, get_db(), Session, AuthenticationFailedError, InvalidSessionError, UserSession (+15 more)

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

### Community 27 - "tsconfig.app.json"
Cohesion: 0.15
Nodes (13): compilerOptions, noUncheckedIndexedAccess, paths, tsBuildInfoFile, exclude, extends, include, @/* (+5 more)

### Community 28 - ".prettierrc.json"
Cohesion: 0.33
Nodes (5): printWidth, $schema, semi, singleQuote, tabWidth

## Knowledge Gaps
- **86 isolated node(s):** `$schema`, `eslint`, `typescript`, `unicorn`, `oxc` (+81 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TaskCreate` connect `Community 0` to `Community 3`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `ApiInternalServerError` connect `Community 3` to `Community 0`, `Community 4`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `BootstrapSetup` connect `Community 1` to `Community 2`, `Community 3`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Task` (e.g. with `Base` and `IntEnumType`) actually correct?**
  _`Task` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `TaskCreate` (e.g. with `TaskEffort` and `TaskPriority`) actually correct?**
  _`TaskCreate` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `TaskUpdate` (e.g. with `TaskEffort` and `TaskPriority`) actually correct?**
  _`TaskUpdate` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `TaskStatus` (e.g. with `Task` and `TaskCreate`) actually correct?**
  _`TaskStatus` has 10 INFERRED edges - model-reasoned connections that need verification._