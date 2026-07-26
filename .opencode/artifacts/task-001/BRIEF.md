# Atomic Task Movement Corrections

## Status

Approved final scope, 2026-07-26.

## Outcome

`PATCH /api/tasks/{task_id}/move` atomically moves or reorders a task while task
creation and movement serialize position allocation and `IN_PROGRESS` capacity
per team. Lifecycle timestamps describe the current workflow pass, backward
events update the existing counters, invalid client input returns `400`, and
self-anchor requests return the unchanged task with `200`.

## Workflow Policy

`TaskStatus` declaration order is the authoritative workflow order:
`BACKLOG`, `TODO`, `IN_PROGRESS`, `REVIEW`, `DONE`. `BACKLOG` remains a normal
workflow stage. Forward moves advance one applicable stage, except review-disabled
work advances directly from `IN_PROGRESS` to `DONE`; backward moves may cross
stages. A task with `should_review=false` may never enter or remain in `REVIEW`.

Same-status reordering is allowed. A request describing the task's existing
adjacency is intentionally a no-op. A task anchored to itself is also a `200`
no-op and bypasses transition, anchor, and capacity validation after the task has
been locked and refreshed.

## Concurrency Contract

Creation and movement call the same transaction-scoped PostgreSQL advisory lock
with a module-owned namespace and `team_id`. The lock is acquired before capacity
or position reads. Movement refreshes the task after acquiring the lock and before
using its mutable status or position. Endpoint commit or rollback releases the
lock; service and repository operations never commit.

This serializes same-team creation, movement, sparse midpoint allocation,
rebalance, and net entry into `IN_PROGRESS` without blocking other teams.
`IntegrityError` remains a commit-time safety net rather than an expected
allocation mechanism.

## Lifecycle And Counters

| Target | `started_working_at` | `submitted_for_review_at` | `completed_at` |
|---|---|---|---|
| `BACKLOG` | `NULL` | `NULL` | `NULL` |
| `TODO` | `NULL` | `NULL` | `NULL` |
| `IN_PROGRESS` | movement time | `NULL` | `NULL` |
| `REVIEW` | preserve start | movement time | `NULL` |
| `DONE` | preserve start | preserve only after review | movement time |

Every new entry into `IN_PROGRESS` or `REVIEW` records the new movement time.
Returning before review clears the review timestamp; returning from `DONE` clears
completion. A backward move from `REVIEW` increments `returned_count`; a backward
move from `DONE` increments `reopened_count`. Forward and same-status moves do not
change counters, and movement never changes `blocked_count`.

## HTTP Contract

Invalid forward transitions, review-disabled entry into `REVIEW`, and missing,
wrong-team, or wrong-status anchors return `400` through `InvalidTaskError`.
Self-anchor returns `200`. Capacity, position exhaustion, and commit collisions
return `409`; unauthenticated requests return `401`; missing tasks or teams return
`404`; existing membership and inactive-team behavior remains `409`.

## Preserved Design

Do not refactor `BACKLOG`, enum ordering, placement adjacency no-op,
`get_destination_neighbors()`, `rebalance_task_column()`, sparse formulas, the
deferred unique constraint, endpoint-owned transactions, source gaps, generic
repository updates, or the normal-update `REVIEW` guard. No migration, retry
framework, transaction manager, source compaction, or ordering abstraction is
part of this correction.

## Source

- Pull request: https://github.com/DavidHruby1/mantask/pull/19
- Original tracked stage: https://github.com/DavidHruby1/mantask/issues/17
- This approved branch artifact supersedes conflicting lifecycle, counter,
  self-anchor, helper-name, HTTP-status, and concurrency statements in the issue.
