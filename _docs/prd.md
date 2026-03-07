# Mantask (working name)
Task management software for small teams

## Overview
This application is a specialized, developer-centric task and workflow management tool designed for teams. It emphasizes minimizing workflow friction through structured triage (Inbox), actionable "Debriefs" for state regressions, strict Work-in-Progress (WIP) tracking, and deep system integrations (GitLab). It is designed to be lightweight, fast, keyboard oriented, and capable of running efficiently on small self-hosted environments.

---

## User Flows
1. **Onboarding** (admin creates org/workspace -> invite user -> user accepts invite -> selects/joins team -> lands on default kanban -> empty-state shows hotkeys + "create first task" CTA -> user can open Inbox to see "mailbox" empty-state)

2. **Task Triage** (create task -> defaults to Todo -> optionally add description/effort/dates/priority/layers -> assign to someone -> assignee receives Inbox notify (assignee can't clear unclaimed inbox notificaitons) -> assignee can claim it -> task moves to Todo -> task appears in Kanban and List views)

3. **Bulk Triage Mode** - use case: I want to assign multiple different tasks to one person (press bulk mode when creating task -> select assignee -> type many task titles in a queue below each other -> optionally each title has three dots to expand into detail task view: it's gonna be a modal transition -> apply -> tasks are sent into Inbox of the asignee)

4. **Filters Workflow** (click on filter button -> open right sidebar -> apply filters (by layers, state, assignee, etc.) -> clear filters -> return to default kanban view)

5. **Start Work + NOW (first task in WIP)** (Todo -> move task to WIP -> task becomes NOW automatically if it's first in order -> defaultlimit is 2 (can be changed by admin) -> if task moved to WIP when WIP full, rejection and error toast shows -> kanban "Now" status automatically updates)

6. **Submit for Review** (WIP -> Review -> reviewer(s) receive Inbox notification "Task X needs review" -> task shows in Review column -> developer waits)

7a. **Review Approve Path** (reviewer opens Inbox row -> opens task -> approves -> task moves to Done -> developer receives grouped Inbox update -> task shows Done + timestamps recorded)

7b. **Review Return + Debrief Lifecycle** (reviewer moves Review -> Todo or WIP -> must choose return reason (debrief) + optional note -> active debrief created/attached to task -> developer receives Inbox update -> developer works -> when moving WIP -> Review again -> debrief modal forces acknowledgement (Space) -> on successful resubmit -> debrief marked resolved/inactive (history kept, active cleared))

8. **Blocker Handshake** (assignee presses Block -> chooses reason (note) + optional @mention -> task shows blocked flag in its current column -> mentioned person gets exactly one Inbox ping -> mentioned person resolves/unblocks + adds 1-line resolution note -> assignee notified to resume + blocker notified that loop is closed)

9. **Subtasks (Checkbox Extension)** (open task detail -> add subtasks as checkboxes -> check/uncheck as work progresses -> completion updates activity feed -> no state changes required - can not be move to Review/Done if not all subtasks completed)

10. **Reopen Done Task** (user moves Done -> Todo -> must add reopen reason -> "Reopened" badge pinned -> the person who finished it receives Inbox notification (and optionally last reviewer) -> task returns to planning pool)

11. **Inbox Triage Actions** (Inbox row appears grouped by Task ID -> user can Open Task -> Acknowledge/Clear (marks handled) -> Approve (for review items) -> Snooze 1 day (hides row until snoozed_until) -> snoozed row reappears later at top)

12. **Focus Mode Notifications** (user enables Focus Mode -> no toast notifications -> all events still go to Inbox -> only exception: if explicitly @mentioned as a Blocker -> silent red badge on Inbox icon appears)

---

## Functionality 

### Hierarchy
- Organization is the one instance of the app running on a certain VPS and domain
- Each organization can have teams that are isolated from each other and have different members
- Each team has one shared kanban board that displays all tasks
- Layers are a flexible tagging/filtering system applied to tasks (e.g., #frontend, #api, #devops, #docs) to organize work without requiring rigid project structures

### Setup
### Instance Bootstrap (First-Time Setup)
- One domain = one Organization (one installation equals one workspace)
- When the app is deployed on a fresh VPS and database contains zero users, the instance is considered "unclaimed"
- If `users_count == 0`, the root URL shows **Create Owner Account** screen instead of Login
- First registered user automatically becomes `Owner` (Admin role with full permissions)
- During first registration:
    - Organization record is created (singleton, exactly one per install) if it does not already exist
    - Owner is linked to this Organization
    - Default Team (e.g. "Main") is automatically created
    - Owner is automatically added as a member of the default Team
- After the first user is created, public registration is permanently disabled
- From that moment on, new users can only join via invitation links generated by an Admin
- If database already contains at least one user, accessing `/register` redirects to Login
- Organization-level settings (name, logo, global WIP limit, timezone, integrations) are stored in a singleton Organization record

### Register & Login
- Owner must have VPS and domain to run this app on
- In the team management settings, admin can create invitation link that can be used to invite new person to the organization
    - Admin can also invite a member of one team to another
- Since this app is self-hosted, user will have to create new account for each organization
- User has to type email and password for creation
- There is gonna be 'forgot password' feature to renew the password if forgotten
- After successful operation, user will be prompted to enter his username that others will see
- After making new account using the link for joining the organization, user will see the main kanban of the team that he was invited to
- If user doesn't logout, the session is active for 30 days. After that if there is no activity - logout. Each time user opens the app and is active, the timer resets to 30 days.

### Menu
- Top-left is gonna be a small card with user's profile picture, name and organization he is in
- Under that there is a small tab with text "Teams" and rolldown button that expands the tab
- There user can switch teams and admin can manage teams
- Menu is gonna be in a form of buttons with icons and tooltips on hover
- In the menu there is these buttons:
    - `Add Task`
    - `Inbox`
    - `Layers`
    - `Scratchpad`
    - `Worklog`
    - `Analytics`
    - `Settings`
- Admin will also see some more options:
    - `Integrations`
    - `Roles`
- Admin will also have more right than other members, like creating layers for example
- Each menu button will be described later in this document

### Account Settings
- Change picture, username
- Logout
- Delete account
- Select default team/layer, default view
- Light / Dark mode

### Kanban / List
- There is 4 columns: 'Todo', 'In Progress (WIP)', 'Review', 'Done'
- User won't be able to create more or delete one
- When it grows too large, scrollbars will appear
- Moving tasks in different state is used by mouse dragging or keyboard shortcut - user must focus the task first tho
- Tasks are displayed across all layers in a single unified kanban; use the Filters sidebar to narrow by layer or chips

### Adding a Task
- There is gonna be 2 ways to create a task:
    - 1. Pressing the menu button
    - 2. Keyboard shortcut

**Pressing the menu button:**
- It will show modal in the middle with Title and option to add description below
- Then priority (optional) -> Low, Medium, High, Urgent). Each priority gives a color distinciton. If none selected, color is gonna be neutral (gray)
- Two optional dates:
    - Review Date: Date at which the task has to be prepared for review in 'Review'
    - Due Date: Hard limit of when the task has to be in 'Done'
- Assignee - choose who will be the task send to. If omitted, it's gonna be assigned to the creator
- Layers (optional, multi-select) - tag the task with one or more layers (e.g., #frontend, #api) for organization and filtering
- There can be also note added which is a text field for the creator to pass any meaningful info
- User can choose where the task should go to: 'Todo', WIP or 'Review', default is 'Todo'. 'Done' is not possible
- There is also possibility turning off the need to be reviewed, because standard behaviour of the app is that every task needs to be first approved in 'Review' to then go to 'Done', but omitting this in the task creation, it can be placed to 'Done' right away from WIP
- Possibility to add comments or attach files

**Keyboard shortcut:**
- It shows the same modal, just the trigger event is different
- User can bind it himself, but default is 'n' as 'new'

**Bulk Triage Mode:**
- Button in task creation modal
- Switches to a Modal that has only one text field for adding task title
- First has to select assignee, because this is used when there is a need for multiple task for specific person. If not assigned, it's assigned to the creator.
- Optionally select layer(s) to apply to all tasks in the batch
- Then creator can start typing titles and on pressing 'Enter' another text field for another title creates below and so on
- There is three dots on the right side of each text field enabling creator to go in detail for that prompt
- There is gonna be animation that makes the modal grow and switches the content for the settings of that particular task, just like it was described in the task creation
- There will also be a button to go back (arrow) that will make the modal shrink back to its original size and switch content for the bulk triage mode
- When all done, tasks are sent into the Inbox of the assignee, and if its assigned to the creator, they end up in 'Todo'

### Inbox
- Central system and communication layer for this app
- Each notificatoin is one row, it's exactly like an email inbox
- Assigned tasks are there and can be claimed
- Its divided into two panels. Left one is smaller and is the email inbox. Right one shows the opened row in detail so user can read the full message there, see the full task, etc.
- Once the notification is resolved, it is removed and archived. User can view the archive when switching to archive tab

### Roles
- Admin, Member, Reviewer, Guest
- Horoable mention: Owener - is one layer above admin; owner is automatically admin; can create more admins

**Admin (Owner / Manager):**
- Full system access. Sees "Roles" and "Integrations" in the Settings page 
​- Tasks: Can create, edit, delete, assign, and force-move any task across any layer
- Settings: Can invite/revoke users, change user roles, set global WIP limits, create/manage layers, and configure GitLab webhooks/integrations
- Overrides: Can bypass system guardrails (e.g., forcing a blocked task to move or overriding a debrief loop with an admin note)
​
**Member (Standard Developer):**
- Standard workspace access (Inbox, Kanban, Layers, Scratchpad, Worklog, Analytics)
- Tasks: Can create tasks, use Bulk Triage, edit task details, assign tasks to themselves or others, and tag tasks with layers
- Workflow: Can move tasks through all standard states (Todo → WIP → Review → Done) and trigger Debriefs or Blockers
- Restrictions: Cannot access system integrations, invite new users, or change global team settings (like WIP limits), create layers

**Reviewer (External Contractor / QA):**
- Limited workspace access. Can view kanban, tasks, and Inbox notifications filtered by assigned layers
- Tasks: Cannot create new tasks or use Bulk Triage
​- Workflow: Strictly limited to the "Review" phase. Can approve tasks (Review → Done) or reject tasks triggering a Debrief (Review → Todo/WIP). Cannot move tasks into WIP or pull tasks from Todo
- Interaction: Can comment on tasks and participate in Blocker handshakes if @mentioned
​
**Guest (Client / Stakeholder):**
- Strictly read-only
- Visibility: Can view the Kanban/List boards filtered by assigned layers, task details, and public comments to track progress
- Restrictions: Cannot create, edit, assign, or move tasks. Cannot comment, approve reviews, or interact with Blockers. Does not receive Inbox notifications for workflow state changes

### Layers
- Flexible tagging system that organizes tasks within a team's kanban without creating separate boards
- Admin can create, rename, and archive layers
- Tasks can be tagged with only one layer
- For quick filtering, layers are shown as chips above the kanban to cycle through quickly
- They can also be selected and filtered from the right sidebar 
- Default layer view can be set per user (selected by default when opening kanban)

### Scratchpad
- Private sandbox to dump unstructured thoughts during meetings or brainstorming, which can later be converted into tasks
- Acts as a simple, persistent, personal Markdown text editor
- One-liner with limited amount of words
- On the right, there is button "Convert" which will open Add Task modal
- Note that it will be placed into the active team and can be tagged with layers during conversion!

### Blocker Handshake
- Triggered by pressing 'b' on a focused task or clicking the "Block" button
- User must write a 1-line note as a reason of why it is blocked
- Optional: @mention someone who needs to unblock it
- Once blocked, a red badge appear on the task card without changing its column. On hover over the badge shows the reason note
- The @mentioned person gets an Inbox ping (bypasses standard Focus Mode silence) and the whole team gets a batched update
- System logs a blocked_at timestamp to quietly calculate total block duration without active timers
- Blocked tasks show up under the global "Blocked" filter
- Anyone can unblock the task, but they are forced to write a short resolution note (min 1 word)
- Unblocking logs the unblocked_at timestamp and pins the resolution note to the task history
- The original assignee and the person who created the block both receive an unblock notification to resume work
- Total blocked_time per task is shown in the task details, and weekly block counts will show in Analytics (deep reason-analytics are out of scope for V1)

### Focus Mode
- When focus mode is on, user won't get notified. The inbox is still active, user just won't be interrupted
- User can turn it on in the top bar - simple toggle or keyboard shortcut
- Exception (Blockers): If the user is explicitly @mentioned in a Blocker Handshake, the system still does not show a toast, but it forces a silent red badge to appear on the left-nav Inbox icon, signaling that a teammate is hard-blocked waiting on them.
- Other members see the user is using focus mode

### Review
- Strict quality gate between 'WIP' and 'Done' - every task requires explicit approval unless "No Review Required" was set during creation  
- Moving `WIP → Review` logs `submitted_for_review_at`, frees WIP slot, makes task structurally read-only, and sends Inbox notification to assigned reviewer (reviewer can be anyone who gets set by admin) 
- Only Reviewer and Admin can decide outcome: `Approve (Review → Done)` or `Return (Review → Todo/WIP)`  
- Approve logs `approved_at` + `approved_by`, moves task to `Done`, and notifies original assignee with grouped Inbox update  
- Return requires selecting structured reason (debrief) and optional note; logs `returned_at`, moves task back, and creates exactly one active Debrief attached to the task  
- Active Debrief must be acknowledged (Space confirmation modal) before task can be resubmitted `WIP → Review`; on resubmit, Debrief is marked resolved (history preserved)  
- Review decisions are binary - no soft states, no partial approvals, no silent edits; comments allowed but do not replace decision  
- Review tasks show reviewer avatar(s), submission timestamp, and "Returned X times" badge; 'Done' shows approval metadata  
- Review items appear in Inbox grouped by Task ID; reviewers can Open, Approve, or Clear after decision  
- Admin can override `Review → Done` with mandatory visible admin note (fully logged in task history)  

### Debrief System
- Records exactly why a task gets sent backwards the moment it happens, so the team stops making the same mistakes without needing meetings

**Review Return (Review → Todo/WIP):** 
- Solves the silent rework loop by forcing clear feedback
- Reviewer must pick a reason (Missing tests, Spec unclear, Edge cases, Style) + optional 1-line note
- Reason pins permanently to the task as a banner
- Developer must hit `[Space]` to explicitly acknowledge the debrief before resubmitting
- Guardrail can only be bypassed by an Admin override with a written note

**Blocker Debrief (Press 'b'):** 
- Exposes hidden waiting time by forcing dependencies into the open
- Assignee selects a reason (Waiting for review, Dependency, CI broken) + optional @mention and note
- Places a visible red flag on the task board
- @mentioned user gets exactly 1 Inbox ping and resolves it via a 1-line reply from their Inbox (strictly no chat threads)

**Reopen Debrief (Done → Todo):** 
- Tracks quality blindness by categorizing why finished work bounced back
- User must pick a reopen reason (Bug remains, Regression, Missing requirement) + optional 1-line note
- Permanently pins a "Reopened" badge to the task card

### Worklog
- A simple timeline showing exactly what was finished, who did it, and when
- Strictly a history log, not an analytics or math tool. The original task is always the source of truth
- Automatically creates a permanent entry only when a task reaches 'Done' (from Review, or straight from WIP)
- Saves the task link, layers, finisher's name, exact time, if it was reviewed, and how many times it bounced back
- Entries are completely locked (immutable) and cannot be edited
- Displays as a Calendar view (day, week, or month)
- Can be quickly filtered by user, layer, or date
- Clicking any log entry opens the full task details
- At the end of each day, completed tasks in 'Done' and tasks in 'Review' will be logged in the Worklog and removed from kanban

### Analytics
- Built entirely from `task_events` log (state changes, review transitions, block/unblock) - no metrics stored statically; all values calculated at query time  
- Core timestamps tracked:
    - `created_at (t1)`
    - `wip_entered_at (t2)`
    - `review_entered_at (t3)` 
    - `done_at (t4)`, plus `blocked_at / unblocked_at` per cycle  
- Time metrics: 
    - `coding_time (t3 - t2)`,
    - `cycle_time (t4 - t2)`
    - `lead_time (t4 - t1)`
    - `review_wait` (total time in Review)
    - `blocked_time` (sum of all block intervals)  
- Quality metrics: `rework_count` (number of Review → WIP/Todo returns per task) and weekly `avg_rework_count` to expose instability  
- Effort system: XS / S / M / L / XL mapped to `1 / 2 / 3 / 5 / 8` points (relative effort, not hours)  
- Weekly commitment tracking: `effort_committed_per_week` (points entering WIP) vs `effort_delivered_per_week` (points reaching Done)  
- `over_commitment_ratio = committed / delivered` (>1.0 signals over-promising; visible as warning indicator)  
- Throughput metrics: raw `throughput_per_week` (tasks completed) and `avg_cycle_time` across tasks done that week  
- Velocity chart: X-axis = week number, Y-axis = effort_delivered_per_week, with rolling N-week average line as baseline for forecasting  
- Forecasting rule: large features estimated by dividing total effort points by rolling average velocity (e.g., 36 points / 12 pts/week ≈ 3 weeks)  

### Filters & Sort
- Opens as a right sidebar in the kanban view
- Filters are single seleciton by default
- Filters can be combined if user holds Shift or Ctrl
-> There will be informational tooltip showing this to the user
- Clear filters resets to default kanban state
- When filtering by state, non-selected columns are hidden and remaining columns align from the right
- User can create their favorite filters that will be placed at the top

#### Single Filters
- By status
    - Todo
    - WIP / In Progress
    - Review
    - Done
- By derived state / overlays
    - Now
    - Blocked now
    - Ever blocked
    - Returned at least once
    - Never returned
    - Reopened
- By creator
    - Select from list
    - Search by name / username / email
- By assignee
    - Select from list
    - Search by name / username / email
    - Unassigned
- By reviewer
    - Select from list
    - Search by name / username / email
    - No reviewer
- By effort
    - 1
    - 2
    - 3
    - 5
    - 8
    - No effort set
- By creation date
    - Exact date
    - Before
    - After
    - Between range
    - Older than X
    - Created today
    - Created yesterday
    - Created last week
    - Created last month
- By review date
    - Exact date
    - Before
    - After
    - Between range
    - Review due today
    - Review due this week
    - Review overdue
    - No review date
- By due date
    - Exact date
    - Before
    - After
    - Between range
    - Due today
    - Due this week
    - Overdue
    - No due date
- By completion
    - Completed today
    - Completed yesterday
    - Completed last week
    - Completed last month
    - Completed in date range
- By priority
    - None
    - Low
    - Medium
    - High
    - Urgent
    - No priority set
- By review flag
    - Review required
    - No review required
- By time in WIP
    - Greater than X
    - Less than X
    - Between range
- By time in review
    - Greater than X
    - Less than X
    - Between range
- By layer
    - Exact layer
    - Multiple layers
    - No layer
- By returned and reopen count
    - Returned once
    - Returned 2 times
    - Returned more than X times
    - Returned exactly N times
    - Returned at least N times
- By text search
    - Title
    - Description
    - Title + description

#### Combined Filters
- Mixing status and derived state filters will be forbidden
- Predicted most used combinations (for composite indexes):
    - 2 Branches: 1. Starting with status filter, 2. Not starting with status filter
    - Second will be often creator/assignee/reviewer
    - Third will be often time filtering

### Settings
- Central configuration hub divided into: General, Teams, Layers, Roles, Integrations (Admin only where applicable)

- **General**
    - Organization name and branding (logo upload)
    - Global WIP limit (default = 2, adjustable by Admin)
    - Default task behavior (Review required by default: On/Off)
    - Timezone and week start day (affects Worklog & Analytics aggregation)

- **Teams**
    - Create / rename / archive teams    - Set default reviewer(s) per team
    - Move members between teamse default landing layer for new members
    - Set default reviewer(s) per team
    - Define default landing view for new members

- **Layers**    - Set layer visibility and permissions (if needed)
    - Create / rename / archive layersyers into groups (optional)
    - Set layer descriptions and color coding
    - Organize layers hierarchically (optional parent-child relationships)
    - Configure visibility per team Member / Reviewer / Guest)
    - Grant or revoke Reviewer capability per team
- **Roles**ead-only overview)
    - Assign and change user roles (Admin / Member / Reviewer / Guest)
    - Grant or revoke Reviewer capability per team
    - View role permission matrix (read-only overview)vite links

- **Invitations**    - View pending invites and their status
    - Generate time-limited invite links
    - Revoke active invitation links
    - View pending invites and their status picture
    - Select default team / layer view / view type (Kanban or List)
- **Account Preferences (Personal)**ight / Dark mode
    - Change username and profile picturee Focus Mode by default
    - Select default team / project / view (Kanban or List)
    - Toggle Light / Dark mode
    - Enable / disable Focus Mode by default
    - Set default snooze duration
- **Notifications**
    - Configure Inbox grouping behavior
    - Set default snooze duration

- **Security**    - Force logout from all devices
    - Change passwordversible, requires password confirmation)
    - View active sessions
    - Force logout from all devices
    - Delete account (irreversible, requires password confirmation)
    - Export Analytics data (CSV)
- **Data & Logs (Admin)**estore database snapshot (manual trigger)
    - View system event logs (task_events stream)


### Integrations
- *Not a priority for now, will be added as the last feature*