import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
    {
        path: '/',
        redirect: { name: 'dashboard' },
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('@/views/Login.vue'),
    },
    {
        path: '/bootstrap',
        name: 'bootstrap',
        component: () => import('@/views/Bootstrap.vue'),
    },
    {
        path: '/dashboard',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
    },
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
})

// Refreshes server-backed auth state before choosing the route.
// Each auth state has one valid entry route, which prevents redirect loops.
router.beforeEach(async (target) => {
    if (target.name === 'bootstrap') return true

    const auth = useAuthStore()
    await auth.loadStatus()

    if (!auth.bootstrapped) {
        return target.name === 'bootstrap' ? true : { name: 'bootstrap' }
    }

    if (!auth.authenticated) {
        return target.name === 'login' ? true : { name: 'login' }
    }

    if (target.name === 'login' || target.name === 'bootstrap') {
        return { name: 'dashboard' }
    }
})

export default router
