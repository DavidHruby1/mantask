import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { TeamRead } from '@/interfaces'

import { teamsApi } from '@/api/teams'


export const useTeamsStore = defineStore('teams', () => {
    const currentUserTeams = ref<TeamRead[]>([])

    async function getCurrentUserTeams(): Promise<TeamRead[]> {
        const currUserTeams = await teamsApi.getCurrentUsersTeams()
        currentUserTeams.value = currUserTeams
        return currUserTeams
    }

    return {
        currentUserTeams,
        getCurrentUserTeams
    }
})
