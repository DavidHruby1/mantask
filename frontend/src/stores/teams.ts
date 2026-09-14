import { ref, watch } from 'vue'
import { defineStore } from 'pinia'
import type { TeamRead } from '@/interfaces'

import { teamsApi } from '@/api/teams'
import { useAuthStore } from '@/stores/auth'

export const useTeamsStore = defineStore('teams', () => {
    const authStore = useAuthStore()
    const currentUserTeams = ref<TeamRead[]>([])
    const selectedTeamId = ref<number | null>(null)
    let activeRequestController: AbortController | null = null

    watch(selectedTeamId, (teamId) => {
        const userId = authStore.currentUser?.id
        if (userId === undefined || teamId === null) return

        try {
            localStorage.setItem(
                `mantask.selectedTeamId.${userId}`,
                String(teamId),
            )
        } catch (error) {
            console.warn('Could not save selected team:', error)
        }
    })

    async function getCurrentUserTeams(): Promise<TeamRead[] | undefined> {
        activeRequestController?.abort()
        const controller = new AbortController()
        activeRequestController = controller

        try {
            const teams = await teamsApi.getCurrentUsersTeams(controller.signal)
            if (controller.signal.aborted) return

            currentUserTeams.value = teams
            return teams
        } catch (error) {
            if (controller.signal.aborted) return
            throw error
        } finally {
            if (activeRequestController === controller) {
                activeRequestController = null
            }
        }
    }

    function initializeSelectedTeam(teams: TeamRead[]): void {
        const userId = authStore.currentUser?.id
        if (userId === undefined) return

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

        selectedTeamId.value = storedTeam?.id ?? privateTeam?.id ?? null
    }

    function reset(): void {
        activeRequestController?.abort()
        activeRequestController = null
        currentUserTeams.value = []
        selectedTeamId.value = null
    }

    return {
        currentUserTeams,
        selectedTeamId,
        getCurrentUserTeams,
        initializeSelectedTeam,
        reset,
    }
})
