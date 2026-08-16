<script setup lang="ts">
import { ref } from 'vue'
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
} from '@lucide/vue'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
// Clicking on the user profile shows modal, therefore another emit is needed
// All the modals are in the Layout template, just invisible until called through emits

// Clicking the sidebar expand button emits event to the parent
// The parent then changes the flex values

// Switching teams also emits event
// The parent then changes loaded tasks
// **I need to adjust backend endpoint for this**

// Clicking on the "Add task" button also emits event, that opens modal
// The parent then sends the task data to the backend and store gets updated,
// which will show the new tasks in Kanban

// Clicking on the nav items emits it to the parent
// Then the RouterView changes the view according to the button

const emit = defineEmits<{
    (e: 'toggle-sidebar'): void
}>()

defineProps<{
    collapsed: boolean
}>()

const selectedNavItem = ref<number>(0)
const selectedTeam = ref<string>('Team A')

function handleNavItemClick(event: MouseEvent) {
    const button = event.currentTarget

    if (!(button instanceof HTMLButtonElement)) return

    selectedNavItem.value = Number(button.id)
}

</script>

<template>
    <div class="flex flex-col bg-atmosphere-gradient mx-2 my-2 rounded-lg p-1 overflow-hidden">
        <div
            class="flex items-center gap-3 mt-2 mb-4 px-1.5"
        >
            <div
                class="w-7 h-7 shrink-0 rounded-sm bg-white-base"
                aria-hidden="true"
            ></div>
            <div
                class="whitespace-nowrap transition-opacity duration-200"
                :class="collapsed ? 'opacity-0' : 'opacity-100'"
            >
                <span class="font-medium text-white-base">David Hruby</span>
            </div>
        </div>

        <button
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
            <!-- placeholder for teams (later use v-for and existing teams from db) -->
            <div class="flex flex-col gap-2 py-3 px-4 bg-black w-32 rounded-lg">
                <span class="text-white-base">Team 1</span>
                <span class="text-white-base">Team 2</span>
                <span class="text-white-base">Team 3</span>
                <span class="text-white-base">Team 4</span>
            </div>
        </DropdownMenu>

        <nav class="flex flex-col flex-1 gap-1 mt-32" aria-label="Dashboard navigation">
            <button
                type="button"
                aria-label="Add task"
                class="
                    w-full flex items-center gap-3 rounded-lg py-1.5 px-2 overflow-hidden
                    hover:bg-atmosphere-light focus-visible:bg-atmosphere-light active:bg-atmosphere-light
                "
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
            <button
                id="1"
                type="button"
                aria-label="Kanban"
                class="w-full flex items-center gap-3 rounded-lg py-1.5 px-2 overflow-hidden hover:bg-atmosphere-light focus-within:bg-atmosphere-light"
                :class="selectedNavItem === 1 ? 'bg-atmosphere-light' : ''"
                @click="handleNavItemClick"
            >
                <LayoutDashboard
                    :size="24"
                    :stroke-width="1.5"
                    color="var(--color-white-base)"
                    class="shrink-0"
                />
                <span
                    class="text-white-base whitespace-nowrap transition-opacity duration-200"
                    :class="collapsed ? 'opacity-0' : 'opacity-100'"
                >Kanban</span>
            </button>
            <button
                id="2"
                type="button"
                aria-label="Inbox"
                class="w-full flex items-center gap-3 rounded-lg py-1.5 px-2 overflow-hidden hover:bg-atmosphere-light focus-within:bg-atmosphere-light"
                :class="selectedNavItem === 2 ? 'bg-atmosphere-light' : ''"
                @click="handleNavItemClick"
            >
                <Inbox
                    :size="24"
                    :stroke-width="1.5"
                    color="var(--color-white-base)"
                    class="shrink-0"
                />
                <span
                    class="text-white-base whitespace-nowrap transition-opacity duration-200"
                    :class="collapsed ? 'opacity-0' : 'opacity-100'"
                >Inbox</span>
            </button>
            <button
                id="3"
                type="button"
                aria-label="Scratchpad"
                class="w-full flex items-center gap-3 rounded-lg py-1.5 px-2 overflow-hidden hover:bg-atmosphere-light focus-within:bg-atmosphere-light"
                :class="selectedNavItem === 3 ? 'bg-atmosphere-light' : ''"
                @click="handleNavItemClick"
            >
                <NotebookPen
                    :size="24"
                    :stroke-width="1.5"
                    color="var(--color-white-base)"
                    class="shrink-0"
                />
                <span
                    class="text-white-base whitespace-nowrap transition-opacity duration-200"
                    :class="collapsed ? 'opacity-0' : 'opacity-100'"
                >Scratchpad</span>
            </button>
            <button
                id="4"
                type="button"
                aria-label="Analytics"
                class="w-full flex items-center gap-3 rounded-lg py-1.5 px-2 overflow-hidden hover:bg-atmosphere-light focus-within:bg-atmosphere-light"
                :class="selectedNavItem === 4 ? 'bg-atmosphere-light' : ''"
                @click="handleNavItemClick"
            >
                <ChartLine
                    :size="24"
                    :stroke-width="1.5"
                    color="var(--color-white-base)"
                    class="shrink-0"
                />
                <span
                    class="text-white-base whitespace-nowrap transition-opacity duration-200"
                    :class="collapsed ? 'opacity-0' : 'opacity-100'"
                >Analytics</span>
            </button>
            <button
                id="5"
                type="button"
                aria-label="Settings"
                class="
                    w-full flex items-center gap-3 rounded-lg mt-auto py-1.5 px-2 overflow-hidden
                    mb-2 hover:bg-atmosphere-light focus-within:bg-atmosphere-light
                "
                :class="selectedNavItem === 5 ? 'bg-atmosphere-light' : ''"
                @click="handleNavItemClick"
            >
                <Settings
                    :size="24"
                    :stroke-width="1.5"
                    color="var(--color-white-base)"
                    class="shrink-0"
                />
                <span
                    class="text-white-base whitespace-nowrap transition-opacity duration-200"
                    :class="collapsed ? 'opacity-0' : 'opacity-100'"
                >Settings</span>
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
