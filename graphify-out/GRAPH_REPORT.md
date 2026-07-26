# Graph Report - mantask  (2026-07-26)

## Corpus Check
- 51 files · ~9,498 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 312 nodes · 615 edges · 40 communities (29 shown, 11 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 43 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `02c7deda`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tasks.py
- auth.py
- teams.py
- TaskService
- auth.py
- tasks.py
- bootstrap.py
- team.py
- Input.vue
- Form.vue
- 2d4c6e8f0a1b_add_backlog_task_status.py
- 4f6a8b0c2d3e_normalize_task_positions.py
- main.ts
- Button.vue
- Container.vue
- Heading.vue
- Link.vue
- Text.vue
- counter.ts
- CurrentSessionDep
- Response
- UserSession
- bootstrap.py
- tasks.py
- datetime
- Session
- Task
- TaskCreate
- TaskFilters
- TaskStatus

## God Nodes (most connected - your core abstractions)
1. `AppError` - 19 edges
2. `TaskStatus` - 16 edges
3. `TaskEffort` - 15 edges
4. `Base` - 14 edges
5. `TaskPriority` - 13 edges
6. `Team` - 13 edges
7. `TeamMember` - 13 edges
8. `TaskCreate` - 13 edges
9. `Task` - 12 edges
10. `User` - 12 edges

## Surprising Connections (you probably didn't know these)
- `upgrade()` --indirect_call--> `TaskEffort`  [INFERRED]
  backend/alembic/versions/83e5ec226cc6_initial_migration.py → backend/app/models/enums.py
- `AppConfig` --uses--> `Base`  [INFERRED]
  backend/app/models/app_config.py → backend/app/core/db.py
- `Task` --uses--> `TaskStatus`  [INFERRED]
  backend/app/models/task.py → backend/app/models/enums.py
- `Task` --uses--> `TaskPriority`  [INFERRED]
  backend/app/models/task.py → backend/app/models/enums.py
- `Task` --uses--> `TaskEffort`  [INFERRED]
  backend/app/models/task.py → backend/app/models/enums.py

## Import Cycles
- None detected.

## Communities (40 total, 11 thin omitted)

### Community 0 - "tasks.py"
Cohesion: 0.10
Nodes (36): delete_task(), get_task(), get_tasks(), move_task(), patch_task(), post_task(), CurrentSessionDep, DbSessionDep (+28 more)

### Community 1 - "auth.py"
Cohesion: 0.11
Nodes (24): get_current_session(), DbSessionDep, SessionTokenDep, UserSession, auth_user(), login(), logout(), DbSessionDep (+16 more)

### Community 2 - "teams.py"
Cohesion: 0.16
Nodes (29): Base, get_db(), Session, TeamType, UserRole, Persist a team task while enforcing lifecycle and board-position invariants., Task, TeamMember (+21 more)

### Community 3 - "TaskService"
Cohesion: 0.13
Nodes (18): Validate and stage editable task fields while preserving review consistency., Apply the configured count-based capacity rule shared by creation and movement., Reject a status change that violates the board's workflow policy.          Enum, Derive lifecycle timestamps and backward-event counters from one move instant., Allocate a positive distinct sparse position, or signal exhausted integer space., Coordinate one policy-complete move while leaving transaction completion to the, Validate task membership, then serialize capacity and sparse append allocation., TaskService (+10 more)

### Community 4 - "auth.py"
Cohesion: 0.22
Nodes (8): ChangePasswordResult, LoginInput, LoginResult, BaseModel, Self, RegisterInput, RegisterResult, ResetPasswordResult

### Community 5 - "tasks.py"
Cohesion: 0.29
Nodes (3): upgrade(), IntEnumType, TypeDecorator

### Community 6 - "bootstrap.py"
Cohesion: 0.16
Nodes (17): AppAlreadyBootstrappedError, AppError, AuthenticationFailedError, InvalidBootstrapSecretError, InvalidSessionError, InvalidTaskError, NoActiveTeamSelectedError, NotAuthenticatedError (+9 more)

### Community 7 - "team.py"
Cohesion: 0.38
Nodes (4): BaseModel, TeamCreate, TeamRead, TeamUpdate

### Community 8 - "Input.vue"
Cohesion: 0.29
Nodes (5): InputProps, inputType, inputVariants, isPasswordVisible, props

### Community 9 - "Form.vue"
Cohesion: 0.40
Nodes (5): emit, FormProps, formVariants, handleSubmit(), props

### Community 10 - "2d4c6e8f0a1b_add_backlog_task_status.py"
Cohesion: 0.40
Nodes (4): downgrade(), Add BACKLOG recoverably because PostgreSQL 11 cannot use a new enum value transa, Remove BACKLOG without rewriting task data, refusing downgrade while rows use it, upgrade()

### Community 11 - "4f6a8b0c2d3e_normalize_task_positions.py"
Cohesion: 0.40
Nodes (4): downgrade(), Preserve visible column order while creating sparse, safely bounded positions., Restore the TODO default and non-deferrable uniqueness without densifying positi, upgrade()

### Community 13 - "Button.vue"
Cohesion: 0.50
Nodes (3): ButtonProps, buttonVariants, props

### Community 14 - "Container.vue"
Cohesion: 0.50
Nodes (3): attrs, containerVariants, forwardedAttrs

### Community 15 - "Heading.vue"
Cohesion: 0.50
Nodes (3): HeadingProps, headingVariants, props

### Community 16 - "Link.vue"
Cohesion: 0.50
Nodes (3): LinkProps, linkVariants, props

### Community 17 - "Text.vue"
Cohesion: 0.50
Nodes (3): props, TextProps, textVariants

### Community 32 - "bootstrap.py"
Cohesion: 0.18
Nodes (13): bootstrap_setup(), bootstrap_status(), DbSessionDep, Response, AppConfig, create_app_config(), get_in_progress_limit(), is_bootstrapped() (+5 more)

### Community 33 - "tasks.py"
Cohesion: 0.18
Nodes (19): count_team_tasks_by_status(), find_tasks(), get_destination_neighbors(), get_last_task_position(), get_task_by_id(), insert_task(), lock_task_positions(), datetime (+11 more)

## Knowledge Gaps
- **25 isolated node(s):** `ButtonProps`, `props`, `buttonVariants`, `attrs`, `forwardedAttrs` (+20 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `BootstrapSetup` connect `bootstrap.py` to `teams.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `TaskStatus` (e.g. with `Task` and `TaskCreate`) actually correct?**
  _`TaskStatus` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `TaskEffort` (e.g. with `upgrade()` and `Task`) actually correct?**
  _`TaskEffort` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Base` (e.g. with `AppConfig` and `Task`) actually correct?**
  _`Base` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `TaskPriority` (e.g. with `Task` and `TaskCreate`) actually correct?**
  _`TaskPriority` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Validate task membership, then serialize capacity and sparse append allocation.`, `Validate and stage editable task fields while preserving review consistency.`, `Apply the configured count-based capacity rule shared by creation and movement.` to the rest of the system?**
  _50 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tasks.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1026827012025902 - nodes in this community are weakly interconnected._