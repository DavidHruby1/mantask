# Residual Risks

- **Advisory locks are cooperative.** Any future same-team capacity or position
  writer that omits `lock_task_positions()` can reintroduce races. The task
  repository helper and module documentation identify the required coordination
  point; the unique constraint remains a final position safety net.
- **One team is the serialization scope.** Concurrent task creation and movement
  in one team wait behind each other even when touching different columns. This
  is intentional because the same lock protects team-wide `IN_PROGRESS` capacity;
  unrelated teams do not block each other.
- **Rebalance is an `O(n)` destination write.** It remains atomic and uses the
  explicitly deferred position constraint, but a large exhausted column can hold
  the team lock longer. Automatic retry and source compaction remain out of scope.
- **Commit conflicts remain possible outside cooperating task writes.** Endpoint
  `IntegrityError` mapping stays as a `409` safety net and clients must refetch;
  collisions are not used as ordinary allocation control flow.
- **PostgreSQL-specific coordination.** Two-key transaction advisory locks and
  explicit constraint deferral intentionally couple movement to PostgreSQL.
- **Existing BACKLOG downgrade is not clean on PostgreSQL 16.** A disposable
  `alembic downgrade base` reached the pre-existing enum-removal revision and
  failed while changing `tasks.status` from `task_status_with_backlog` back to
  `task_status` because PostgreSQL attempted an equality operation across the
  two enum types. The transaction rolled back and `upgrade head` remained clean.
  The confirmed correction scope explicitly keeps the BACKLOG migration unchanged.
