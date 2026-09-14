import { api } from '@/api/client'

import type { TeamRead } from '@/interfaces'

export const teamsApi = {
    async getCurrentUsersTeams(signal?: AbortSignal): Promise<TeamRead[]> {
        const response = await api.get<TeamRead[]>('/api/teams', { signal })
        return response.data
    }
}
