import { createRouter, createWebHistory } from 'vue-router'
import { useSessionStore } from '@/stores/session'

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

// Refreshes server-backed session state before choosing the route.
// Each session state has one valid entry route, which prevents redirect loops.
router.beforeEach(async (target) => {
    const session = useSessionStore()
    await session.loadStatus()

    if (!session.bootstrapped) {
        return target.name === 'bootstrap' ? true : { name: 'bootstrap' }
    }

    if (!session.authenticated) {
        return target.name === 'login' ? true : { name: 'login' }
    }

    if (target.name === 'login' || target.name === 'bootstrap') {
        return { name: 'dashboard' }
    }
})

export default router
