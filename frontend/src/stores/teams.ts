import { ref, watch } from 'vue'
import { defineStore } from 'pinia'
import type { TeamRead } from '@/interfaces'

import { teamsApi } from '@/api/teams'


export const useTeamsStore = defineStore('teams', () => {
    const currentUserTeams = ref<TeamRead[]>([])
    const selectedTeamId = ref<number | null>(null)
    const initializedUserId = ref<number | null>(null)

    watch(selectedTeamId, (teamId) => {
        if (initializedUserId.value === null || teamId === null) return

        try {
            localStorage.setItem(
                `mantask.selectedTeamId.${initializedUserId.value}`,
                String(teamId),
            )
        } catch (error) {
            console.warn('Could not save selected team:', error)
        }
    })

    async function getCurrentUserTeams(): Promise<TeamRead[]> {
        const currUserTeams = await teamsApi.getCurrentUsersTeams()
        currentUserTeams.value = currUserTeams
        return currUserTeams
    }

    function initializeSelectedTeam(userId: number, teams: TeamRead[]): void {
        let storedTeamId: number | null = null
        try {
            const storedValue = localStorage.getItem(`mantask.selectedTeamId.${userId}`)
            if (storedValue !== null) {
                storedTeamId = Number(storedValue)
            }
        } catch (error) {
            console.warn('Could not restore selected team:', error)
        }

        const activeTeams = teams.filter((team) => team.is_active)
        const storedTeam = activeTeams.find((team) => team.id === storedTeamId)
        const privateTeam = activeTeams.find((team) => team.type === 'private')

        initializedUserId.value = userId
        selectedTeamId.value = storedTeam?.id ?? privateTeam?.id ?? null
    }

    return {
        currentUserTeams,
        selectedTeamId,
        getCurrentUserTeams,
        initializeSelectedTeam,
    }
})
