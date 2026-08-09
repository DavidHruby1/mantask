import type { RouteLocationRaw } from 'vue-router'

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

export interface ButtonProps {
    variant?: 'glass' | 'ghost'
    size?: 'sm' | 'md' | 'lg'
    type?: 'button' | 'submit' | 'reset'
    disabled?: boolean
}

export interface FormProps {
    variant?: 'transparent' | 'card'
    loading?: boolean
    novalidate?: boolean
}

export interface HeadingProps {
    variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
    color?: 'primary' | 'secondary'
}

export interface InputProps {
    size?: 'sm' | 'md' | 'lg'
    type?: 'text' | 'number' | 'email' | 'password'
    placeholder?: string
    disabled?: boolean
    required?: boolean
    error?: string
}

export interface LinkProps {
    to: RouteLocationRaw
    color?: 'primary' | 'secondary'
    size?: 'xs' | 'sm' | 'md' | 'lg'
}

export interface TextProps {
    color?: 'primary' | 'secondary'
    size?: 'xs' | 'sm' | 'md' | 'lg'
}
