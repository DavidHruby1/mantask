# Task Move Endpoint

## Problem

The kanban board needs a backend endpoint for dragging tasks between status
columns and reordering within columns. The existing `PATCH /tasks/{task_id}`
handles field updates only — it does not support status transitions or position
changes.

## Desired Outcome

A single `PATCH /tasks/{task_id}/move` endpoint that accepts `TaskMove` (already
defined in `schemas/task.py`) and atomically updates the task's status, position,
and related timestamps using sparse integer positions to avoid O(n) reordering
on every move.

## Domain Terms

- **Anchor task**: The task that the moved task will be placed immediately
  *after* in the target column. Computations use the anchor and the *next* task
  after it.
- **Sparse position**: An integer assigned at large intervals (1000-step) so
  that insertion between two tasks can compute a midpoint without touching other
  rows.
- **Rebalance**: When sparse gaps are exhausted (integer division yields a
  duplicate position), all tasks in the target status column are reassigned
  sequential 1000-step positions, then the move is retried.

## Scope

- New endpoint: `PATCH /tasks/{task_id}/move` (body: `TaskMove`)
- Refactor task creation position assignment to use sparse positions (1000-step
  increments) instead of the current sequential (1, 2, 3…) scheme.
- The `TaskMove` schema gains no new fields beyond what already exists.

## Constraints & Invariants

### Position Rules

| Scenario | Formula |
|---|---|
| Anchor provided, next exists after anchor in target column | `(anchor.pos + next.pos) / 2` |
| Anchor provided, anchor is the last task in target column (no next) | `anchor.pos + 1000` |
| `anchor_task_id = None` (place at beginning) | `first_task.pos / 2` |
| Target column is empty | `1000` |

- Position must be unique within `(team_id, status)` (enforced by existing DB
  constraint `uq_task_team_status_position`).
- On collision (computed position equals an existing task's position), rebalance
  the entire status column to 1000, 2000, 3000, …, then retry.
- New task creation assigns `last_task_position + 1000` (first task in column
  gets `1000`).

### Status Transitions

**Forward** (linear, one permitted skip):

| From | To | Condition |
|---|---|---|
| TODO | IN_PROGRESS | always |
| IN_PROGRESS | REVIEW | `should_review = true` |
| IN_PROGRESS | DONE | `should_review = false` |
| REVIEW | DONE | always |

All other forward transitions (TODO → REVIEW, TODO → DONE, etc.) are rejected
with 400.

**Backward**: any transition allowed (IN_PROGRESS→TODO, REVIEW→IN_PROGRESS,
REVIEW→TODO, DONE→TODO, DONE→IN_PROGRESS, DONE→REVIEW).

**Same-status**: reordering within a column allowed (`target_status ==
current_status`).

### IN_PROGRESS Limit

Enforced on net-increase into IN_PROGRESS (moving from TODO, REVIEW, or DONE
into IN_PROGRESS). Same-status reorder within IN_PROGRESS skips the check.
Uses existing `_can_create_in_progress_task()` logic with `get_in_progress_limit()`.

### Timestamps

All timestamp changes are automatic based on the target status:

| Trigger | Action |
|---|---|
| Enter IN_PROGRESS | Set `started_working_at = now()` |
| Target status is not IN_PROGRESS | Clear `started_working_at = NULL` |
| Enter REVIEW | Set `submitted_for_review_at = now()` |
| Target status is TODO or IN_PROGRESS | Clear `submitted_for_review_at = NULL` |
| REVIEW → DONE | Keep the existing `submitted_for_review_at` |
| Enter DONE | Set `completed_at = now()` |
| Target status is not DONE | Clear `completed_at = NULL` |
| Same-status reorder | No timestamp changes |

### Counters

`returned_count`, `reopened_count`, and `blocked_count` are not modified by
this endpoint. Future features will handle these.

### Authorization

- Same `get_accessible_task()` check as all other task endpoints: task exists,
  team exists, team active, user is team member.
- Anchor task (when provided) is validated: must belong to the same team and
  have the same `target_status` as the request. If `anchor_task_id == task_id`,
  treat as a no-op (return 200 with current task).

### No-op Behavior

A move is a no-op (skip DB write, return 200 with current `TaskRead`) when:
- `anchor_task_id == task_id`, or
- The computed position equals the task's current position AND `target_status
  == current_status`.

### Response

- Success: `200` with `TaskRead` of the moved (or unchanged) task.
- Validation and access errors: `400` (invalid transition or anchor), `401`
  (unauthenticated), `404` (missing task or team), and `409` (membership,
  inactive team, IN_PROGRESS limit, or commit conflict), matching existing task
  endpoint behavior.

## Rejected Alternatives

- **Sequential shift on every move**: O(n) per move, poor UX for large columns.
- **Float positions**: Requires DB migration, loses integer simplicity.
- **Separate endpoint for status-only change**: Unnecessary; the move endpoint
  subsumes status transitions.
- **Merging move into existing `PATCH /tasks/{task_id}`**: Pollutes `TaskUpdate`
  with position fields and mixes fundamentally different operations.
- **Keeping submitted_for_review_at on backward transition**: Conflicts with
  existing DB constraint. Keeping it would require a migration and muddles the
  column's intent (current-cycle tracking, not history).

## Acceptance Criteria

1. `PATCH /tasks/{task_id}/move` accepts `TaskMove` body and returns `TaskRead`.
2. Creating new tasks assigns positions at 1000-step increments (1000, 2000, …)
   instead of sequential 1, 2, 3, ….
3. Moving between columns computes position via divide-by-2 or +1000 as defined
   above, and updates status + timestamps correctly.
4. Same-status reordering in an empty column gives position 1000.
5. Moving with `anchor_task_id = None` places the task at the beginning of the
   target column.
6. Moving to the end of a non-empty column (anchor is last task) places after
   it at `anchor.pos + 1000`.
7. When integer division exhausts all gaps, the service rebalances the column
   and retries the move atomically.
8. Invalid forward transitions (e.g., TODO→REVIEW or TODO→DONE) are
   rejected with 400.
9. All backward transitions (e.g., DONE→TODO, REVIEW→TODO) are accepted.
10. Moving into IN_PROGRESS from a non-IN_PROGRESS status is blocked with 409
    when the team's IN_PROGRESS limit is reached.
11. Reordering within IN_PROGRESS does not trigger the limit check.
12. Timestamps (`started_working_at`, `submitted_for_review_at`, `completed_at`)
    are set on enter and cleared on leave of the corresponding status.
13. No-op moves (same position, same status, or anchor == moved task) return
    200 without DB writes.
14. Anchor validation: reject if anchor belongs to different team or different
    target_status.
15. Access control matches existing task endpoints.
