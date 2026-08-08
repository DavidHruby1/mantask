import { ref } from 'vue'
import { defineStore } from 'pinia'

import { sessionApi } from '@/api/session'

export const useSessionStore = defineStore('session', () => {
    const bootstrapped = ref<boolean | null>(null)
    const authenticated = ref<boolean | null>(null)

    // Refreshes the bootstrap and authentication state used for routing.
    // Values are updated together so a failed request cannot leave a partial new state.
    async function loadStatus() {
        if (bootstrapped.value !== true) {
            const bootstrapStatus = await sessionApi.getBootstrapStatus()

            if (!bootstrapStatus.bootstrapped) {
                bootstrapped.value = false
                authenticated.value = false
                return
            }
        }

        const loginResult = await sessionApi.getLoginResult()

        bootstrapped.value = true
        authenticated.value = loginResult.authenticated
    }

    return {
        bootstrapped,
        authenticated,
        loadStatus,
    }
})
