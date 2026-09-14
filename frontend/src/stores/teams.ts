import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { TeamRead } from '@/interfaces'

import { teamsApi } from '@/api/teams'

export const useTeamsStore = defineStore('teams', () => {
    const currentUserTeams = ref<TeamRead[]>([])
    const selectedTeamId = ref<number | null>(null)
    let preferenceUserId: number | null = null
    let activeRequestController: AbortController | null = null

    function selectTeam(teamId: number | null): void {
        selectedTeamId.value = teamId

        if (preferenceUserId === null || teamId === null) return

        try {
            localStorage.setItem(
                `mantask.selectedTeamId.${preferenceUserId}`,
                String(teamId),
            )
        } catch (error) {
            console.warn('Could not save selected team:', error)
        }
    }

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

    function initializeSelectedTeam(userId: number): void {
        preferenceUserId = userId

        let storedTeamId: number | null = null
        try {
            const storedValue = localStorage.getItem(`mantask.selectedTeamId.${userId}`)
            if (storedValue !== null) {
                storedTeamId = Number(storedValue)
            }
        } catch (error) {
            console.warn('Could not restore selected team:', error)
        }

        const activeTeams = currentUserTeams.value.filter((team) => team.is_active)
        const storedTeam = activeTeams.find((team) => team.id === storedTeamId)
        const privateTeam = activeTeams.find((team) => team.type === 'private')

        selectTeam(storedTeam?.id ?? privateTeam?.id ?? null)
    }

    function reset(): void {
        activeRequestController?.abort()
        activeRequestController = null
        currentUserTeams.value = []
        selectedTeamId.value = null
        preferenceUserId = null
    }

    return {
        currentUserTeams,
        selectedTeamId,
        getCurrentUserTeams,
        initializeSelectedTeam,
        selectTeam,
        reset,
    }
})
