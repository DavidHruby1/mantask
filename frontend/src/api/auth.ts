import axios from 'axios'

import type {
    BootstrapResult,
    BootstrapSetup,
    BootstrapStatus,
    LoginResult,
} from '@/interfaces'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true
})

export const authApi = {
    async getBootstrapStatus(): Promise<BootstrapStatus> {
        const response = await api.get<BootstrapStatus>('/api/bootstrap/status')
        return response.data
    },
    async getLoginResult(): Promise<LoginResult> {
        const response = await api.get<LoginResult>('/api/auth/me')
        return response.data
    },
    async bootstrapSetup(payload: BootstrapSetup): Promise<BootstrapResult> {
        const response = await api.post<BootstrapResult>('/api/bootstrap/setup', payload)
        return response.data
    }
}
