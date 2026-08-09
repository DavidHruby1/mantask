import axios from 'axios'
import { ref } from 'vue'
import { defineStore } from 'pinia'

import { authApi } from '@/api/auth'
import type { BootstrapSetup, LoginInput } from '@/interfaces'

export const useAuthStore = defineStore('auth', () => {
    const bootstrapped = ref<boolean | null>(null)
    const authenticated = ref<boolean | null>(null)

    // Refreshes the bootstrap and authentication state used for routing.
    // Values are updated together so a failed request cannot leave a partial new state.
    async function loadStatus() {
        if (bootstrapped.value !== true) {
            const bootstrapStatus = await authApi.getBootstrapStatus()

            if (!bootstrapStatus.bootstrapped) {
                bootstrapped.value = false
                authenticated.value = false
                return
            }
        }

        try {
            const authResult = await authApi.getAuthResult()

            bootstrapped.value = true
            authenticated.value = authResult.authenticated
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 401) {
                bootstrapped.value = true
                authenticated.value = false
                return
            }

            console.error(
                'Failed to load authentication status:',
                error instanceof Error ? error.message : 'Unknown error',
            )
            throw error
        }
    }

    // Submits the initial application setup and updates the auth state after the server creates a session.
    // It returns false after logging a failure so the calling view can stay on the form without duplicating error handling.
    async function bootstrap(payload: BootstrapSetup): Promise<boolean> {
        try {
            const result = await authApi.bootstrapSetup(payload)

            bootstrapped.value = result.bootstrapped
            authenticated.value = true

            return true
        } catch (error) {
            console.error(
                'Bootstrap setup failed:',
                error instanceof Error ? error.message : 'Unknown error',
            )
            return false
        }
    }

    async function login(payload: LoginInput): Promise<boolean> {
        try {
            const result = await authApi.login(payload)

            authenticated.value = result.authenticated

            return result.authenticated
        } catch (error) {
            authenticated.value = false

            console.error(
                'Login failed:',
                error instanceof Error ? error.message : 'Unknown error',
            )
            return false
        }
    }

    return {
        bootstrapped,
        authenticated,
        loadStatus,
        bootstrap,
        login,
    }
})
