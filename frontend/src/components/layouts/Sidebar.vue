<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useTeamsStore } from '@/stores/teams'
import {
    LayoutDashboard,
    Users,
    ChartLine,
    CirclePlus,
    Inbox,
    NotebookPen,
    PanelLeftClose,
    PanelLeftOpen,
    Settings,
    Power,
} from '@lucide/vue'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import type { AllowedStatus } from '@/interfaces'

const emit = defineEmits<{
    (e: 'toggle-sidebar'): void
    (e: 'add-task', status: AllowedStatus | null): void
}>()

defineProps<{
    collapsed: boolean
    canExpand: boolean
}>()

const authStore = useAuthStore()
const teamsStore = useTeamsStore()
const { currentUser } = storeToRefs(authStore)
const { currentUserTeams } = storeToRefs(teamsStore)
const router = useRouter()

const selectedNavItem = ref<number>(1)
const selectedTeam = ref<string>('')

const navItems = [
    { id: 1, label: 'Kanban', icon: LayoutDashboard, to: { name: 'kanban' } },
    { id: 2, label: 'Inbox', icon: Inbox },
    { id: 3, label: 'Scratchpad', icon: NotebookPen },
    { id: 4, label: 'Analytics', icon: ChartLine },
    { id: 5, label: 'Settings', icon: Settings },
]

function onSelectTeam(teamName: string) {
    if (teamName === selectedTeam.value) return
    selectedTeam.value = teamName
}

async function logout() {
    if (await authStore.logout()) {
        await router.push({ name: 'login' })
    }
}

onMounted(async () => {
    const [user, teams] = await Promise.all([
        authStore.getCurrentUser(),
        teamsStore.getCurrentUserTeams()
    ])
    selectedTeam.value = teams.find(
        (team) => team.id === user?.last_active_team_id
    )?.name ?? ''
})

</script>

<template>
    <div class="flex min-w-0 flex-col bg-atmosphere-gradient p-1 rounded-lg">
        <div
            class="flex items-center gap-3 mt-2 mb-4 px-1.5"
        >
            <div
                class="w-7 h-7 shrink-0 rounded-sm bg-white-base"
                aria-hidden="true"
            ></div>
            <div
                class="min-w-0 overflow-hidden whitespace-nowrap transition-opacity duration-200"
                :class="collapsed ? 'opacity-0' : 'opacity-100'"
            >
                <span
                    class="font-medium text-white-base"
                >
                    {{ currentUser?.username ?? '' }}
                </span>
            </div>
        </div>

        <button
            v-if="canExpand"
            type="button"
            class="flex px-2"
            :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
            @click="emit('toggle-sidebar')"
        >
            <component
                :is="collapsed ? PanelLeftOpen : PanelLeftClose"
                :size="24"
                :stroke-width="1.5"
                color="var(--color-white-base)"
                class="shrink-0"
                aria-hidden="true"
            />
        </button>

        <DropdownMenu
            :text="selectedTeam"
            :icon-only="collapsed"
            :hide-chevron="collapsed"
            text-color="var(--color-white-base)"
            :icon="Users"
            :icon-size="24"
            :icon-stroke-width="1.5"
            icon-color="var(--color-white-base)"
            class="
                w-full mt-2 rounded-lg py-1.5 px-2 text-white-base
                hover:bg-atmosphere-light focus-visible:bg-atmosphere-light
            "
            open-class="bg-atmosphere-light"
        >
            <li
                v-for="team in currentUserTeams"
                :key="team.id"
                @click="onSelectTeam(team.name)"
            >
                {{ team.name }}
            </li>
            <li v-if="currentUserTeams.length === 0" class="text-white-base/60">
                No teams yet.
            </li>
        </DropdownMenu>

        <nav class="flex flex-col flex-1 gap-1 mt-32" aria-label="Dashboard navigation">
            <button
                type="button"
                aria-label="Add task"
                class="
                    w-full flex items-center gap-3 rounded-lg py-1.5 px-2 overflow-hidden
                    hover:bg-atmosphere-light focus-visible:bg-atmosphere-light active:bg-atmosphere-light
                "
                @click="emit('add-task', null)"
            >
                <CirclePlus
                    :size="24"
                    :stroke-width="1.5"
                    color="var(--color-white-base)"
                    class="shrink-0"
                />
                <span
                    class="text-white-base whitespace-nowrap transition-opacity duration-200"
                    :class="collapsed ? 'opacity-0' : 'opacity-100'"
                >Add task</span>
            </button>
            <component
                v-for="item in navItems"
                :key="item.id"
                :is="item.to ? RouterLink : 'button'"
                v-bind="item.to
                    ? { to: item.to }
                    : { type: 'button' }"
                :aria-label="item.label"
                class="
                    w-full flex items-center gap-3 rounded-lg py-1.5 px-2 overflow-hidden
                    text-white-base hover:bg-atmosphere-light focus-visible:bg-atmosphere-light
                "
                :class="{
                    'bg-atmosphere-light': selectedNavItem === item.id,
                    'mt-auto': item.id === 5,
                }"
                @click="selectedNavItem = item.id"
            >
                <component
                    :is="item.icon"
                    :size="24"
                    :stroke-width="1.5"
                    class="shrink-0"
                    aria-hidden="true"
                />
                <span
                    class="whitespace-nowrap transition-opacity duration-200"
                    :class="collapsed ? 'opacity-0' : 'opacity-100'"
                >{{ item.label }}</span>
            </component>
            <button
                type="button"
                aria-label="Logout"
                class="
                    w-full flex items-center gap-3 rounded-lg mb-2 py-1.5 px-2 overflow-hidden
                    hover:bg-atmosphere-light focus-visible:bg-atmosphere-light
                "
                @click="logout"
            >
                <Power
                    :size="24"
                    :stroke-width="1.5"
                    color="var(--color-white-base)"
                    class="shrink-0"
                />
                <span
                    class="text-white-base whitespace-nowrap transition-opacity duration-200"
                    :class="collapsed ? 'opacity-0' : 'opacity-100'"
                >Logout</span>
            </button>
        </nav>
    </div>
</template>

<style scoped>
button:focus,
button:focus-visible {
    outline: none;
    box-shadow: none;
}
button {
    cursor: pointer;
}
</style>
