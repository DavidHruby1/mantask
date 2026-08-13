export interface BootstrapStatus {
    bootstrapped: boolean
}

export interface BootstrapSetup {
    username: string
    email: string
    password: string
    organization_name: string
    team_name: string
    bootstrap_secret: string
}

export interface BootstrapResult {
    bootstrapped: boolean
    active_team_id: number | null
}

export interface LoginInput {
    email: string
    password: string
}

export interface LoginResult {
    authenticated: boolean
    active_team_id: number | null
    session_token: string | null
}

export interface FormErrors {
    [field: string]: string
}

export enum TaskPriority {
    LOW = "low",
    MEDIUM = "medium",
    HIGH = "high",
    URGENT = "urgent",
}

export enum TaskEffort {
    XS = 1,
    S = 2,
    M = 3,
    L = 5,
    XL = 8,
}

export enum TaskStatus {
    BACKLOG = 'backlog',
    TODO = 'todo',
    IN_PROGRESS = 'in_progress',
    REVIEW = 'review',
    DONE = 'done',
}

export interface TaskCreate {
    assignee_member_id?: number | null
    reviewer_member_id?: number | null
    title: string
    description?: string | null
    layer?: string | null
    priority?: TaskPriority | null
    review_date?: string | null
    due_date?: string | null
    effort?: TaskEffort | null
    should_review?: boolean
    status?: TaskStatus.BACKLOG | TaskStatus.TODO | TaskStatus.IN_PROGRESS
}

export interface TaskUpdate {
    assignee_member_id?: number | null
    reviewer_member_id?: number | null
    title?: string
    description?: string | null
    layer?: string | null
    priority?: TaskPriority | null
    review_date?: string | null
    due_date?: string | null
    effort?: TaskEffort | null
    should_review?: boolean
}

export interface TaskRead {
    id: number
    team_id: number
    creator_member_id: number
    assignee_member_id: number | null
    reviewer_member_id: number | null
    title: string
    description: string | null
    layer: string | null
    priority: TaskPriority | null
    review_date: string | null
    due_date: string | null
    effort: TaskEffort | null
    should_review: boolean
    status: TaskStatus
    position: number
    created_at: string
    updated_at: string
    started_working_at: string | null
    submitted_for_review_at: string | null
    completed_at: string | null
    returned_count: number
    reopened_count: number
    blocked_count: number
}

export interface TaskMove {
    target_status: TaskStatus
    anchor_task_id: number | null
}
