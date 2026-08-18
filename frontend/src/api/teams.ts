import { api } from '@/api/client'

import type { TeamRead } from '@/interfaces'

export const teamsApi = {
    async getCurrentUsersTeams(): Promise<TeamRead[]> {
        const response = await api.get<TeamRead[]>('/api/teams')
        return response.data
    }
}
