import { ref } from 'vue'
import { defineStore } from 'pinia'

import { authApi } from '@/api/auth'

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

        const loginResult = await authApi.getLoginResult()

        bootstrapped.value = true
        authenticated.value = loginResult.authenticated
    }

    return {
        bootstrapped,
        authenticated,
        loadStatus,
    }
})
