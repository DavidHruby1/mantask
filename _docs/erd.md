# Entity-Relationship Diagram for MVP

## Frist version ERD

Table app_config {
    id smallint [pk, default: 1]
    name text [not null]
    wip_limit int [not null, default: 2]

    Note: 'Checks: id = 1; wip_limit > 0'
}

Table team {
    id int [pk, increment]
    name text [not null]
}

Table app_user {
    id int [pk, increment]
    username text [not null]
    email text [not null, unique]
    password_hash text [not null]
    timezone text [not null, default: 'UTC']
}

Table team_member {
    team_id int [not null]
    user_id int [not null]
    role text [not null, default: 'member']
    joined_at timestamptz [not null, default: `now()`]

    indexes {
        (team_id, user_id) [pk]
    }
}

Table task {
    id int [pk, increment]
    team_id int [not null]
    creator_id int [not null]
    assignee_id int
    reviewer_id int
    layer text
    title text [not null]
    description text
    status text [not null, default: 'todo']
    priority text [not null, default: 'none']
    position int [not null]
    review_date date
    due_date date
    effort smallint
    should_review boolean [not null, default: true]
    created_at timestamptz [not null, default: `now()`]
    started_working_at timestamptz
    submitted_for_review_at timestamptz
    completed_at timestamptz
    returned_count int [not null, default: 0]
    reopened_count int [not null, default: 0]
    blocked_count int [not null, default: 0]
}

Table session {
    id int [pk, increment]
    user_id int [not null]
    created_at timestamptz [not null, default: `now()`]
    last_seen_at timestamptz [not null, default: `now()`]
    expires_at timestamptz [not null, default: `now() + INTERVAL '30 days'`]

    Note: 'Check: created_at < expires_at'
}

Ref: team_member.team_id > team.id [delete: cascade]
Ref: team_member.user_id > app_user.id [delete: restrict]

Ref: task.team_id > team.id [delete: cascade]
Ref: session.user_id > app_user.id [delete: cascade]

Ref: task.(team_id, creator_id) > team_member.(team_id, user_id) [delete: restrict]
Ref: task.(team_id, assignee_id) > team_member.(team_id, user_id) [delete: restrict]
Ref: task.(team_id, reviewer_id) > team_member.(team_id, user_id) [delete: restrict]
