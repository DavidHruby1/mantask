# Mantask Product Requirements Document

**Status:** Product direction | **Audience:** Self-hosted delivery teams with 2-15
members | **Updated:** 2026-08-20

## 1. Product

Mantask is a radically simple project-management tool for small teams. It combines a
fixed Kanban with optional short-term planning, collaborative Markdown notes, time
tracking, and structured learning.

> Plan briefly. Finish clearly. Learn from reality.

Mantask occupies the space between simple task tools that lack coordination and broad
PM suites that require teams to configure and maintain their own system. It should be
useful within minutes, without custom statuses, views, fields, or methodology setup.

## 2. Users

The primary customer is a 3-12 person team that regularly plans, executes, and reviews
shared work. Mantask supports roughly 2-15 members per team.

Initial users include small software teams, agencies, design and content teams,
internal operations teams, and privacy-conscious teams preferring self-hosting.

Mantask is not designed for enterprise portfolios, arbitrary workflows, large-scale
resource planning, regulated accounting, payroll, or autonomous AI management.

## 3. Principles

1. **Simplicity is the edge.** Every concept must justify its mental cost.
2. **The core is fixed.** Teams use Mantask instead of configuring Mantask.
3. **Advanced features are optional.** Disabled modules remain invisible.
4. **Coordination loops close.** Reviews and blockers have a next actor and outcome.
5. **Plans meet reality.** Original scope and estimates remain visible.
6. **Analytics describe work, not workers.** No employee productivity rankings.
7. **Teams own their data.** Self-hosting, backup, and export are first-class.
8. **Frequent actions are fast.** The product is keyboard-oriented and low-friction.

## 4. Non-Goals

- Custom statuses, workflow builders, or per-project workflows.
- Epics, initiatives, portfolios, or deep hierarchies.
- Gantt charts, critical paths, dependencies, or resource leveling.
- Built-in chat or a general-purpose wiki/database builder.
- Mandatory Scrum ceremonies or recurring sprint machinery.
- Employee monitoring, payroll, invoices, taxes, or timesheet approvals.
- AI features in the active roadmap.
- An automation or plugin marketplace.

## 5. Product Model

| Concept | Purpose |
| --- | --- |
| Team | Shared members, settings, and work |
| Workspace | Selected Team or private work context |
| Layer | Persistent workstream or tag, such as `#client-acme` or `#frontend` |
| Task | Smallest owned unit of executable work |
| Milestone | Optional time-bounded delivery package inside one Layer |
| Scratchpad | Shared or private Markdown documents linked to work |
| Time Entry | Billable or non-billable time recorded against a Task |
| Worklog | Immutable history of meaningful events |
| Debrief | Short reflection producing one learning action |

Rules:

- A Task belongs to one Workspace and may have multiple Layers.
- A Task belongs to at most one Milestone.
- A Milestone has one home Layer and may contain many Tasks.
- Assigning a Task to a Milestone adds its home Layer to the Task.
- Multiple Milestones may run concurrently and involve multiple people.
- Milestones never create a second Task workflow.

## 6. Core Work

### Fixed Kanban

```text
Backlog -> To do -> In progress -> Review -> Done
```

- Columns cannot be added, renamed, removed, or reordered.
- The board shows one Workspace at a time.
- Drag and drop changes state or shared manual order.
- Local filters and sorting never overwrite shared order.
- Completed Tasks remain searchable and are never silently deleted.

### Tasks

A Task has a title, status, creator, and Workspace. Optional properties are Markdown
description, assignee, reviewer, Layers, priority, relative effort, dates, Milestone,
planned hours, comments, attachments, and activity.

A Task has one assignee. Review-required work must have one reviewer before entering
Review. Other work may move directly from In progress to Done.

### Work-In-Progress

WIP counts In progress Tasks per assignee. Teams configure one shared limit:

- `Warn` displays overload but permits the move.
- `Enforce` blocks the move unless an authorized override includes a reason.

WIP is a coordination policy, not an employee score. Review waiting is tracked
separately because Review can become the bottleneck.

### Layers

Layers organize work without separate boards or project hierarchies. A Layer belongs
to one Team, can label many Tasks, and can contain multiple Milestones. Archiving a
Layer preserves its Tasks, Milestones, and history.

## 7. Coordination

### Review Feedback

- Entering Review creates an action for the reviewer.
- Approval moves the Task to Done.
- Returning work requires a reason and a concrete expected correction.
- Feedback remains visible when the Task is resubmitted.
- Repeated returns may trigger a Debrief.

Review Feedback fixes the current Task. A Debrief changes future team behavior.

### Action-Only Inbox

Inbox contains only required actions: assignments, reviews, Blocker responses,
Debriefs, and significant reopened work. Informational events belong to activity.
Completing the underlying action resolves the Inbox item automatically.

### Blocker Handshake

```text
Open -> Acknowledged -> Resolved
```

A Blocker records the problem, requested action, responder, acknowledgement, and
resolution. The Task remains in its current state, may have one active Blocker, and
does not gain a separate chat thread.

### Debrief

A Debrief may follow repeated Review returns, reopened work, a long Blocker, or a
completed Milestone. It asks:

1. What did we expect?
2. What actually happened?
3. What one thing should change next time?

The outcome is one improvement Task, one working-agreement change, or an explicit
decision that no change is needed. Debriefs are concise, asynchronous, and blameless.

## 8. Planning Module

Planning is optional and disabled by default. It adds Milestones, Roadmap, and
Scratchpad planning without changing the Kanban.

### Milestones

A Milestone is a short time-bounded delivery package, not a Scrum sprint. It has a
name, outcome, home Layer, owner, start and end dates, status, Tasks, and optional
planned-hour budget and Scratchpad plan.

Statuses are `Draft`, `Active`, `Completed`, and `Cancelled`.

Activation preserves the original Task scope, estimates, dates, and owner. Later
changes remain allowed but are shown as changes to the plan.

Progress shows Task states, original versus current scope, remaining time, waiting or
blocked work, and planned versus actual hours when available. Logged hours are never
presented as percentage completion.

Before completion, unfinished Tasks must be completed, moved to Backlog, or moved to
another Milestone. Closing records the outcome and a short Debrief.

### Roadmap

Roadmap is a derived timeline, not a separate planning database:

- Rows are Layers and bars are Milestones.
- Bars show dates, status, progress, scope change, and blocked or overdue signals.
- Selecting a bar opens the Milestone.
- Filters include Layer, owner, date range, and status.

Roadmap excludes Task-level Gantt bars, dependencies, critical path, automatic
rescheduling, and resource leveling.

## 9. Scratchpad

Scratchpad contains collaborative Markdown documents for ideas, plans, decisions,
research, and Debriefs.

Documents support Team or private scope, authorship, version history, Layers, stable
links, search, Task/Milestone backlinks, and non-destructive conversion of selected
text or checklist items into Tasks.

Each Milestone may have one primary plan:

```markdown
## Outcome
## Scope
## Out of scope
## Risks and unknowns
## Plan
```

Tasks created from this plan inherit the Milestone and home Layer and retain a source
backlink. Scratchpad has no formulas, relational properties, custom schemas, plugins,
or autonomous content generation.

## 10. Time Tracking Module

Time Tracking is optional and disabled by default. It supports plan-versus-actual
analysis and external client billing.

- Tasks may have planned hours; Milestones may have an hour budget.
- A Time Entry records Task, user, date, duration, billable state, and optional note.
- Manual entry is the initial input method.
- Entries roll up by Task, Milestone, Layer, user, and date.
- Timesheets provide personal, weekly, Team, Milestone, and Layer views.
- Billable records can be exported as CSV.
- Changes to Time Entries are auditable.

Mantask does not initially manage rates, currencies, taxes, invoices, payments,
payroll, or approval chains. Hours are never used as an employee performance score.

## 11. Worklog And Analytics

Worklog preserves meaningful Task, Review, Blocker, Milestone, Debrief, and Time Entry
events. System events are immutable; corrections create new events.

Team analytics may include throughput, cycle time, work age, Review wait, blocked
time, return/reopen rate, Milestone scope change, planned versus actual hours,
billable time, and repeated Debrief causes.

Mantask must not provide employee leaderboards, productivity scores, presence
tracking, response-time rankings, or conclusions equating hours with value.

## 12. Roles And Access

- `Owner`: instance ownership and global settings.
- `Admin`: membership, Layers, modules, and Team policy.
- `Member`: normal work within joined Teams.

Every user has one private Workspace excluded from Team access and reporting. The
first deployment creates an Owner and default Team through protected bootstrap.
Later users join by invitation; public registration remains disabled.

## 13. Quality Requirements

- Common actions feel immediate on modest self-hosted infrastructure.
- Core workflows are keyboard accessible and do not rely on color alone.
- Team and private data isolation is enforced on the server.
- Workflow mutations are transactional and recover cleanly from conflicts.
- Operators can back up, restore, and export their data.
- PostgreSQL is authoritative and upgrades use versioned migrations.
- The initial product is desktop-first.

## 14. Delivery Direction

1. **Core:** bootstrap, Teams, private Workspace, Kanban, Tasks, Layers, WIP,
   filtering, and Review.
2. **Coordination:** Review Feedback, Inbox, Blocker Handshake, and Worklog.
3. **Planning:** Milestones, Scratchpad planning, Task conversion, and Roadmap.
4. **Time and learning:** planned hours, Time Entries, Timesheets, CSV export,
   Milestone close, Debriefs, and Team analytics.

The Core must remain complete when every optional module is disabled.

## 15. Success Measures

- Time from setup to first useful Task.
- Retention of pilot Teams.
- Cycle time and age of active work.
- Review and Blocker waiting time.
- Milestones closed with explicit scope resolution.
- Original versus final scope and planned versus actual hours.
- Repeated rework causes and completed Debrief actions.
- Qualitative reduction in time spent maintaining the PM tool.

Task count, hours per employee, individual completion totals, and online time are not
success measures.

## 16. Future

Potential integrations include GitHub, GitLab, email capture, calendar export,
webhooks, and an API.

AI is excluded from the active roadmap. If considered later, it must operate through
existing Tasks, Scratchpad, Review, Inbox, and Worklog. Consequential actions require
a human owner and must remain scoped, attributable, reviewable, and reversible.
