import { api } from '@/api/client'

import type {
    BootstrapResult,
    BootstrapSetup,
    BootstrapStatus,
    LoginInput,
    LoginResult,
    UserRead,
} from '@/interfaces'


export const authApi = {
    async getBootstrapStatus(): Promise<BootstrapStatus> {
        const response = await api.get<BootstrapStatus>('/api/bootstrap/status')
        return response.data
    },
    async getAuthResult(): Promise<LoginResult> {
        const response = await api.get<LoginResult>('/api/auth/me')
        return response.data
    },
    async getCurrentUser(): Promise<UserRead> {
        const response = await api.get<UserRead>('/api/users/me')
        return response.data
    },
    async bootstrapSetup(payload: BootstrapSetup): Promise<BootstrapResult> {
        const response = await api.post<BootstrapResult>('/api/bootstrap/setup', payload)
        return response.data
    },
    async login(payload: LoginInput): Promise<LoginResult> {
        const response = await api.post<LoginResult>('/api/auth/login', payload)
        return response.data
    },
    async logout(): Promise<LoginResult> {
        const response = await api.post<LoginResult>('/api/auth/logout')
        return response.data
    }
}
