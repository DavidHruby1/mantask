# Task Movement Test Contract

Status: Approved
Approval date: 2026-07-26
Audit: Passed against the confirmed final scope in `BRIEF.md`; no unsupported behavior added.

## Service

### SVC-001 REVIEW re-entry to active work
Given a task in `REVIEW`, when it moves to `IN_PROGRESS`, then `returned_count`
increments, start becomes the movement time, and review/completion timestamps clear.

### SVC-002 REVIEW return before work
Given a task in `REVIEW`, when it moves to `TODO` or `BACKLOG`, then
`returned_count` increments and all lifecycle timestamps clear.

### SVC-003 DONE re-entry to review
Given a task in `DONE`, when it moves to `REVIEW`, then `reopened_count`
increments, completion clears, start is preserved, and review becomes movement time.

### SVC-004 DONE re-entry to active work
Given a task in `DONE`, when it moves to `IN_PROGRESS`, then `reopened_count`
increments, start becomes movement time, and later timestamps clear.

### SVC-005 DONE return before work
Given a task in `DONE`, when it moves to `TODO` or `BACKLOG`, then
`reopened_count` increments and all lifecycle timestamps clear.

### SVC-006 Counter stability
Given a forward transition or same-status reorder, when movement succeeds, then
`returned_count`, `reopened_count`, and `blocked_count` do not change.

### SVC-007 Review eligibility
Given `should_review=false`, when target is `REVIEW`, then `InvalidTaskError` is raised.

### SVC-008 Self-anchor
Given a task anchored to its own ID, when movement is requested, then the locked,
refreshed task is returned without transition, anchor, capacity, or ORM mutation.

### SVC-009 Placement no-op
Given a same-status request matching current adjacency, when movement is requested,
then the task is returned without ORM mutation.

### SVC-010 Invalid client input
Given an invalid forward transition or missing/wrong-team/wrong-status anchor,
when movement is requested, then `InvalidTaskError` is raised.

### SVC-011 Same-status active reorder
Given an `IN_PROGRESS` task reordered within `IN_PROGRESS`, when movement is
validated, then capacity is not read.

## PostgreSQL Integration

### PG-001 Concurrent create allocation
Given two creates in one team/status, when they run concurrently, then both commit
with unique sparse positions.

### PG-002 Concurrent empty-column movement
Given two tasks moving into one empty destination column, when they run concurrently,
then lock serialization produces unique final positions.

### PG-003 Concurrent capacity entry
Given one free `IN_PROGRESS` slot and two entrants, when they run concurrently,
then exactly one enters and the configured limit is not exceeded.

### PG-004 Waiting move refresh
Given a move waiting on the team lock while another transaction changes its task,
when the waiting move acquires the lock, then it refreshes and decides from the new state.

### PG-005 Atomic rebalance
Given an exhausted destination gap, when movement rebalances and commits, then
the final destination positions are unique and ordered atomically.

### PG-006 Constraint mode
Given the task position unique constraint, ordinary duplicate writes fail
immediately, while temporary overlap succeeds only after explicit deferral and
must be unique by commit.

## Endpoint

### API-001 Self-anchor status
Self-anchor returns `200` with current `TaskRead`.

### API-002 Invalid transition status
`InvalidTaskError` from transition validation returns `400`.

### API-003 Invalid anchor status
`InvalidTaskError` from anchor validation returns `400`.

### API-004 Capacity status
An `IN_PROGRESS` capacity conflict returns `409`.

### API-005 Commit collision status
Commit-time `IntegrityError` rolls back and returns `409`.

### API-006 Authentication status
An unauthenticated request returns `401`.

### API-007 Missing resource status
A missing task or team returns `404`.

### API-008 Existing access statuses
Membership and inactive-team failures retain `409`.

### API-009 Success persistence
A normal move commits once, refreshes, and returns `200` with `TaskRead`.
