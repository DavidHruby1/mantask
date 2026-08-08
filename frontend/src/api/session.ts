import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    withCredentials: true
})

export interface BootstrapStatus {
    bootstrapped: boolean
}

export interface LoginResult {
    authenticated: boolean
    active_team_id: number | null
    session_token: string | null
}


export const sessionApi = {
    async getBootstrapStatus(): Promise<BootstrapStatus> {
        const response = await api.get<BootstrapStatus>('/api/bootstrap/status')
        return response.data
    },
    async getLoginResult(): Promise<LoginResult> {
        try {
            const response = await api.get<LoginResult>('/api/auth/me')
            return response.data
        } catch (error) {
            if (axios.isAxiosError(error) &&
                error.response?.status === 401) {
                return {
                    authenticated: false,
                    active_team_id: null,
                    session_token: null
                }
            }

            throw error
        }
    }
}

