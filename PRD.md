# Mantask Product Requirements Document

**Status:** Product direction | **Audience:** Self-hosted delivery teams with 2-15
members | **Updated:** 2026-09-07

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
- Roadmap timelines, Gantt charts, critical paths, automatic scheduling, or resource leveling.
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
| Layer | Shared organization of work, with optional nesting and Milestone Mode |
| Task | Smallest owned unit of executable work |
| Scratchpad | Shared or private Markdown documents linked to work |
| Time Entry | Billable or non-billable time recorded against a Task |
| Worklog | Immutable history of meaningful events |
| Debrief | Short reflection producing one learning action |

Rules:

- A Task belongs to one Workspace and may have multiple Layers.
- Milestone Mode extends a Layer; it is not a separate entity or Task workflow.
- A Task may belong to ordinary Layers and at most one Layer in Milestone Mode.
- Multiple Layers in Milestone Mode may be active concurrently.
- Task dependencies are independent of Layer membership and presentation.

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
description, assignee, reviewer, Layers, priority, relative effort, dates, dependencies,
planned hours, comments, attachments, and activity.

Effort expresses relative difficulty, not calendar duration. It is not automatically
converted into hours, dates, or graphical bar lengths.

A Task has one assignee. Review-required work must have one reviewer before entering
Review. Other work may move directly from In progress to Done.

### Work-In-Progress

WIP counts In progress Tasks per assignee. Teams configure one shared limit:

- `Warn` displays overload but permits the move.
- `Enforce` blocks the move unless an authorized override includes a reason.

WIP is a coordination policy, not an employee score. Review waiting is tracked
separately because Review can become the bottleneck.

### Layers

Layers belong to one Workspace and organize its existing Tasks without separate boards.
The initial hierarchy has two levels: root Layers can represent projects, while child
Layers represent local tags or areas. Hierarchy determines placement, not a separate
project/tag entity type. `#eshop/backend` and `#crm/backend` are distinct Layers.

- Selecting a parent includes Tasks from its children, with each Task shown once.
- Ordinary Layers support multi-selection. A Layer in Milestone Mode is selected alone
    in the initial UI; this filter rule is separate from Task membership.
- `See all tasks` includes Tasks in Layers with Milestone Mode. Their Layer badges
    remain visible; milestone-specific controls appear only on explicit selection.
- Milestone Mode stays in the same Layer navigation, distinguished by color and an
    icon or text label, never color alone. No separate Milestones navigation is needed.
- Archiving a Layer preserves its Tasks and history. Parent inclusion is derived from
    the hierarchy rather than requiring duplicate Task membership in the parent.

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
completed Layer in Milestone Mode. It asks:

1. What did we expect?
2. What actually happened?
3. What one thing should change next time?

The outcome is one improvement Task, one working-agreement change, or an explicit
decision that no change is needed. Debriefs are concise, asynchronous, and blameless.

## 8. Planning Module

Planning is optional and disabled by default. It adds Milestone Mode, Task dependencies,
their graph view, and Scratchpad planning without changing the Kanban. Disabling it
hides planning controls, not Tasks or their Layer membership, and preserves planning data.

### Milestone Mode

A Layer such as `#checkout-mvp` can enable Milestone Mode to coordinate a delivery goal,
not a Scrum sprint. It retains its Layer identity, hierarchy, and Task membership.
It adds an outcome, owner, optional target date, delivery status, and optional hour
budget and primary Scratchpad plan. No planned start date is required.

The outcome states what should be achieved, such as "Customers can pay by card."
The owner coordinates scope, obstacles, and closure, and is not automatically the
assignee of its Tasks. The target date describes the delivery goal, not a Task schedule.

Statuses are `Draft`, `Active`, `Completed`, and `Cancelled`.

Activation preserves the original Task scope, estimates, dates, and owner. Later
changes remain allowed but are shown as changes to the plan.

On explicit selection, a compact header shows completed versus total member Tasks
(for example, `6/10 done`), waiting or blocked work, scope changes, and the target date
when set. Completion counts are not estimates of remaining effort or proof that the
outcome was achieved. Planned versus actual hours are optional, never percentage completion.

Before completion, unfinished Tasks must be explicitly resolved: finish them or remove
them from the delivery scope, recording whether they return to Backlog or move to
another Layer in Milestone Mode. Closing records the outcome and a short Debrief.
Scope history survives membership changes, archival, or disabling Milestone Mode.

### Task Dependencies

- A Task may have multiple predecessors and successors within the same Workspace.
- Task detail provides `Waiting on` with searchable add/remove controls and a derived
    `Blocks` list. Dependencies must be useful without opening a graph.
- Prerequisites are satisfied only when every predecessor is `Done`. An unfinished
    or reopened predecessor shows a warning, but does not block Kanban transitions
    or automatically change the successor's state.
- Dependencies do not create Blocker Handshakes or additional workflow states.
- The server rejects self-links, duplicate links, cross-Workspace links, and cycles,
    including under concurrent changes. Layer membership changes preserve dependencies.

### Dependency Graph MVP

Selecting one Layer in Milestone Mode exposes `Kanban | Dependencies` in the existing
board area. Both views use the same Tasks and states. There is no Roadmap or Gantt view.

- Automatic left-to-right layout shows predecessor-to-successor arrows. Distance is
    not time. Nodes show title, status, assignee, and accessible prerequisite warnings.
- Include all member Tasks, including completed and unconnected ones. Clicking a
    node opens the existing Task detail; relationships are edited there, not by drawing.
- Direct predecessors outside the selected Layer appear as labeled external nodes.
    Do not recursively expand their graph or include them in the Layer's progress.
- Provide pan, zoom, and fit-to-view. Task details and dependency controls remain
    keyboard accessible without requiring graph interaction.
- Layout is derived, not a saved plan. Exclude manual node positioning, graphical
    link editing, date axes, effort-to-time conversion, and automatic rescheduling.

## 9. Scratchpad

Scratchpad contains collaborative Markdown documents for ideas, plans, decisions,
research, and Debriefs.

Documents support Team or private scope, authorship, version history, Layers, stable
links, search, Task/Layer backlinks, and non-destructive conversion of selected
text or checklist items into Tasks.

Each Layer in Milestone Mode may have one primary plan:

```markdown
## Outcome
## Scope
## Out of scope
## Risks and unknowns
## Plan
```

Tasks created from this plan join its Layer and retain a source
backlink. Scratchpad has no formulas, relational properties, custom schemas, plugins,
or autonomous content generation.

## 10. Time Tracking Module

Time Tracking is optional and disabled by default. It supports plan-versus-actual
analysis and external client billing.

- Tasks may have planned hours; Layers in Milestone Mode may have an hour budget.
- A Time Entry records Task, user, date, duration, billable state, and optional note.
- Manual entry is the initial input method.
- Entries roll up by Task, Layer, user, and date, including Layers in Milestone Mode.
- Timesheets provide personal, weekly, Team, and Layer views. Combined Layer totals
    count each Time Entry once even when its Task belongs to multiple selected Layers.
- Billable records can be exported as CSV.
- Changes to Time Entries are auditable.

Mantask does not initially manage rates, currencies, taxes, invoices, payments,
payroll, or approval chains. Hours are never used as an employee performance score.

## 11. Worklog And Analytics

Worklog preserves meaningful Task, dependency, Layer, Milestone Mode, Review, Blocker,
Debrief, and Time Entry events. System events are immutable; corrections create new events.

Team analytics may include throughput, cycle time, work age, Review wait, blocked
time, return/reopen rate, delivery scope change, planned versus actual hours,
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

1. **Core:** bootstrap, Teams, private Workspace, Kanban, Tasks, real Layer identities,
    multi-Layer membership, shallow hierarchy, filtering, WIP, and Review.
2. **Coordination:** Review Feedback, Inbox, Blocker Handshake, and Worklog.
3. **Planning:** Milestone Mode and progress first; Task dependency controls before
    their graph view; Scratchpad planning and Task conversion. No scheduling engine.
4. **Time and learning:** planned hours, Time Entries, Timesheets, CSV export,
    delivery close, Debriefs, and Team analytics.

The Core must remain complete when every optional module is disabled.

## 15. Success Measures

- Time from setup to first useful Task.
- Retention of pilot Teams.
- Cycle time and age of active work.
- Review and Blocker waiting time.
- Layers in Milestone Mode closed with explicit scope resolution.
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
