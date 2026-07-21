# Plan: Atomic Task Movement

## Approved Solution

Implement `PATCH /tasks/{task_id}/move` with sparse integer positions while making position allocation deterministic under PostgreSQL concurrency. Task creation and movement acquire the same transaction-scoped advisory lock keyed by a module namespace and `team_id` before reading IN_PROGRESS capacity or column positions. Target-column reads exclude the moved task. Gap exhaustion is detected from the computed integer position before mutation; the target column is then rebalanced and the position recomputed.

Change `uq_task_team_status_position` to `DEFERRABLE INITIALLY IMMEDIATE`. Move transactions defer that constraint before any possible multi-row rebalance, allowing temporary position overlap while PostgreSQL verifies final uniqueness at commit. Ordinary `flush()` failures are not used as control flow. The trade-offs are one reversible migration and deliberate PostgreSQL coupling in exchange for correct renumbering, empty-column locking, and serialized create/move allocation.

## Inputs

- Brief: `.opencode/artifacts/task-001/BRIEF.md`
- Research: `.opencode/artifacts/task-001/RESEARCH.md`
- Relevant documentation: `docs/backend/onboarding.md`, `docs/backend/modules/tasks.md`, `docs/backend/architecture/backend.md`
- Relevant ADRs: none

## Plan-Wide Safety

- `REVIEW -> IN_PROGRESS` remains an allowed backward transition.
- Final positions remain at least 1 and unique within `(team_id, status)`.
- Every task create or move path acquires the same team-scoped position lock before reading limits or positions.
- A task loaded for endpoint access control is refreshed after the lock is acquired and before move decisions use its mutable state.
- Target-column calculations and rebalance exclude the moved task.
- Same-status reorder does not alter timestamps or consume IN_PROGRESS capacity.
- No-op requests mutate no ORM state and emit no UPDATE.
- Services and repositories never commit; endpoint transaction ownership remains unchanged.
- Generic `IntegrityError` is only a commit-time safety net, not the signal for expected gap exhaustion.
- Existing task counters, `TaskMove`, and unrelated CRUD behavior remain unchanged.

## Pull Requests

### PR 1: Atomic Task Movement

**Outcome:** Authenticated users can atomically move and reorder accessible tasks with correct transitions, timestamps, limits, sparse positions, rebalance, and concurrent allocation safety.

**Work:**

- `backend/app/models/task.py`: declare `uq_task_team_status_position` as `DEFERRABLE INITIALLY IMMEDIATE` so model metadata matches PostgreSQL.
- `backend/alembic/versions/<revision>_make_task_position_unique_deferrable.py`: drop and recreate the named constraint on upgrade; restore the current non-deferrable constraint on downgrade.
- `backend/app/repositories/tasks.py`: add a module-owned advisory-lock namespace, `lock_task_positions(db, team_id)`, one ordered column query accepting `exclude_task_id`, and a helper that defers `uq_task_team_status_position` for the current transaction.
- `backend/app/services/tasks.py`: keep `_can_create_in_progress_task()` unchanged; acquire the team position lock before creation's limit and last-position reads; assign creation positions at `1000` steps.
- `backend/app/services/tasks.py`: add `move_task()` with anchor/self no-op handling, team-lock acquisition, post-lock task refresh, anchor validation, transition validation, serialized IN_PROGRESS net-increase check, target-column loading without the moved task, position computation, proactive gap-exhaustion detection, rebalance to `1000, 2000, ...`, timestamp application, and final ORM mutation.
- `backend/app/services/tasks.py`: compute `1000` when the target list excluding the moved task is empty; otherwise use `first // 2`, `(anchor + next) // 2`, or `anchor + 1000`. Rebalance before mutation when the candidate is below 1 or already occupied, then recompute once.
- `backend/app/api/endpoints/tasks.py`: add `PATCH /{task_id}/move` using `TaskMove`, existing access validation, endpoint-owned commit/rollback/refresh, and existing error types.

**Steps:**

1. Update the model metadata and add the reversible Alembic migration for `DEFERRABLE INITIALLY IMMEDIATE`; verify the constraint remains immediate by default and can be explicitly deferred.
2. Add the repository primitives for the team-scoped transaction lock, ordered target-column loading with `exclude_task_id`, and transaction-level constraint deferral.
3. Update `create_task()` to acquire the shared team lock before the IN_PROGRESS limit and last-position reads, then allocate positions in 1000-step increments without renaming the existing limit helper.
4. Implement `TaskService.move_task()`: handle self-anchor no-op, acquire the team lock, refresh the moved task, validate anchor and transition, enforce net IN_PROGRESS capacity, load the target column without the moved task, compute or rebalance the position, apply timestamps, and mutate the task once.
5. Add `PATCH /tasks/{task_id}/move` with the existing access, commit, rollback, refresh, response, and error-translation conventions.
6. Validate the migration lifecycle, all 15 acceptance criteria, stale-state refresh, advisory-lock serialization, and existing task CRUD behavior.

**Traceability and validation:**

- [ ] Immediate uniqueness remains the default; explicit deferral permits temporary duplicates but rejects duplicate final state at commit.
- [ ] Upgrade, downgrade, and repeated upgrade preserve task data and the constraint name.
- [ ] AC 1: the route accepts `TaskMove`, commits the move, and returns the persisted `TaskRead`.
- [ ] AC 2: creation assigns `1000, 2000, ...` while holding the shared team lock.
- [ ] AC 3-6: cross-column, beginning, end, midpoint, and same-status-empty-after-exclusion scenarios use the brief's formulas.
- [ ] AC 7: an exhausted or invalid gap triggers one deferred-constraint rebalance and recomputation without recovering from failed flush.
- [ ] AC 8: TODO to REVIEW and TODO to DONE return 400.
- [ ] AC 9: IN_PROGRESS to TODO, REVIEW to IN_PROGRESS, REVIEW to TODO, and every DONE backward transition succeed.
- [ ] AC 10-11: only net-increase into IN_PROGRESS can return 409; same-status reorder skips the limit.
- [ ] AC 12: timestamp enter, leave, REVIEW to DONE preservation, DONE to REVIEW reset, and same-status behavior satisfy database constraints.
- [ ] AC 13: self-anchor and unchanged computed placement return 200 without ORM mutation or UPDATE.
- [ ] AC 14: missing, other-team, and wrong-status anchors return 400.
- [ ] AC 15: authentication, membership, inactive-team, and missing-task behavior matches existing task endpoints.
- [ ] Concurrent create and move transactions for one team serialize on the advisory lock and commit unique positions.
- [ ] A move whose task changed while waiting for the advisory lock refreshes that task and applies rules to the post-lock status and position.
- [ ] Existing task CRUD routes retain their current behavior.
- [ ] `python3 -m compileall backend/app` succeeds.

**Dependencies:** None

**Size limit:** Estimated 340 changed logic lines using additions plus deletions. Within the 500-line target; splitting the 60-line constraint migration from its only consumer would add review and sequencing overhead without reducing meaningful cognitive load.

## Residual Risks

- Advisory locks are cooperative rather than schema-enforced. A future position-writing path could omit the lock. Impact: commit-time conflict or limit overrun. Mitigation and owner: the task repository owns the single lock helper, and future task-position changes must use it.
- The migration recreates a unique constraint and therefore takes a PostgreSQL table lock. Impact: brief write interruption during deployment. Mitigation and owner: deployment runs the small constraint migration before feature rollout and verifies lock duration in the target environment.
- PostgreSQL major version is not pinned in the repository. Impact is low because the selected features are longstanding. Mitigation and owner: backend deployment validation records the target version and runs the migration against it before rollout.
