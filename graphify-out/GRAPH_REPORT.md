# Graph Report - mantask  (2026-07-25)

## Corpus Check
- 80 files · ~24,263 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 559 nodes · 983 edges · 45 communities (39 shown, 6 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 34 edges (avg confidence: 0.61)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f0fe9764`
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
- BaseModel
- Functionality
- Research: Task Move Endpoint
- Constraints & Invariants
- Plan: Atomic Task Movement
- Self

## God Nodes (most connected - your core abstractions)
1. `TaskService` - 42 edges
2. `TaskCreate` - 32 edges
3. `TaskUpdate` - 30 edges
4. `Functionality` - 24 edges
5. `AppError` - 19 edges
6. `Task` - 18 edges
7. `BootstrapSetup` - 18 edges
8. `Base` - 15 edges
9. `TaskQuery` - 14 edges
10. `TaskFilters` - 13 edges

## Surprising Connections (you probably didn't know these)
- `AppConfig` --uses--> `Base`  [INFERRED]
  backend/app/models/app_config.py → backend/app/core/db.py
- `post_task()` --references--> `TaskCreate`  [EXTRACTED]
  backend/app/api/endpoints/tasks.py → backend/app/schemas/task.py
- `insert_task()` --references--> `TaskCreate`  [EXTRACTED]
  backend/app/repositories/tasks.py → backend/app/schemas/task.py
- `TaskService` --uses--> `TaskCreate`  [INFERRED]
  backend/app/services/tasks.py → backend/app/schemas/task.py
- `test_task_create_rejects_blank_layer()` --calls--> `TaskCreate`  [EXTRACTED]
  backend/tests/schemas/test_task.py → backend/app/schemas/task.py

## Import Cycles
- None detected.

## Communities (45 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (63): Reject explicit nulls that would violate required task columns., TaskCreate, TaskDelete, TaskFilterFields, TaskFilters, TaskMove, TaskQuery, TaskUpdate (+55 more)

### Community 1 - "Community 1"
Cohesion: 0.13
Nodes (22): bootstrap_setup(), bootstrap_status(), DbSessionDep, Response, AppAlreadyBootstrappedError, InvalidBootstrapSecretError, AppConfig, create_app_config() (+14 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (56): render_item(), run_migrations_offline(), run_migrations_online(), upgrade(), get_current_session(), UserSession, Authenticate activity and persist the renewed server and browser expiry., get_settings() (+48 more)

### Community 3 - "Community 3"
Cohesion: 0.10
Nodes (29): delete_task(), get_task(), get_tasks(), patch_task(), post_task(), CurrentSessionDep, DbSessionDep, # TODO: Task doesn't have to have assignee, it can be picked up by anyone if nob (+21 more)

### Community 4 - "Community 4"
Cohesion: 0.14
Nodes (21): auth_user(), login(), logout(), CurrentSessionDep, DbSessionDep, Response, SessionTokenDep, ApiInternalServerError (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (28): ensure_active_team_id(), get_last_active_team_id(), hash_session_token(), LoginService, Session, UserSession, Keep a usable team selected, falling back to the user's private team., Validate a session and extend its expiry; the caller persists the change. (+20 more)

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
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TaskCreate` connect `Community 0` to `Community 2`, `Community 3`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Why does `TaskUpdate` connect `Community 0` to `Community 3`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `BootstrapSetup` connect `Community 1` to `Community 2`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `TaskService` (e.g. with `TaskCreate` and `TaskFilters`) actually correct?**
  _`TaskService` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Authenticate activity and persist the renewed server and browser expiry.`, `Reject explicit nulls that would violate required task columns.`, `Validate a session and extend its expiry; the caller persists the change.` to the rest of the system?**
  _163 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.059018367961457395 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.12873563218390804 - nodes in this community are weakly interconnected._