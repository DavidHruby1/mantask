import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import { api } from '@/api/client'
import router from './router'
import { useAuthStore } from '@/stores/auth'
import './global.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

api.interceptors.response.use(undefined, async (error) => {
    const authStore = useAuthStore()

    if (error.response?.status === 401 && authStore.authenticated) {
        authStore.reset()
        await router.push({ name: 'login' })
    }

    return Promise.reject(error)
})

app.use(router)

app.mount('#app')
