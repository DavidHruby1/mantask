<script setup lang="ts">
import { ref } from 'vue'
import {
    LayoutDashboard,
    ChartLine,
    CirclePlus,
    Inbox,
    NotebookPen,
    PanelLeftClose,
    Settings,
} from '@lucide/vue'
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

const selectedNavItem = ref<number>(0)


function handleNavItemClick(event: MouseEvent) {
    const button = event.currentTarget

    if (!(button instanceof HTMLButtonElement)) return

    selectedNavItem.value = Number(button.id)
}

</script>

<template>
    <div class="flex flex-col bg-atmosphere-gradient mx-2 my-2 rounded-lg p-1">
        <div class="flex items-center gap-3 p-3">
            <div class="avatar">U</div>
            <div class="flex flex-col">
                <span>David Hrubý</span>
                <span>user@example.com</span>
            </div>
        </div>

        <div class="team-switcher"></div>

        <button
            type="button"
            class="px-2"
            @click="$emit('toggle-sidebar')"
        >
            <PanelLeftClose
                :size="26"
                :stroke-width="1.5"
                color="var(--color-white-base)"
            />
        </button>

        <nav class="flex flex-col flex-1 gap-1" aria-label="Dashboard navigation">
            <div
                class="rounded-lg py-1.5 px-2 hover:bg-atmosphere-light focus-within:bg-atmosphere-light"
            >
                <button
                    type="button"
                    class="w-full flex items-center gap-3"
                >
                    <CirclePlus
                        :size="26"
                        :stroke-width="1.5"
                        color="var(--color-white-base)"
                    />
                    <span class="text-white-base">Add task</span>
                </button>
            </div>
            <div
                class="rounded-lg py-1.5 px-2 hover:bg-atmosphere-light focus-within:bg-atmosphere-light"
                :class="selectedNavItem === 1 ? 'bg-atmosphere-light' : ''"
            >
                <button
                    id="1"
                    type="button"
                    class="w-full flex items-center gap-3"
                    @click="handleNavItemClick"
                >
                    <LayoutDashboard
                        :size="26"
                        :stroke-width="1.5"
                        color="var(--color-white-base)"
                    />
                    <span class="text-white-base">Kanban</span>
                </button>
            </div>
            <div
                class="rounded-lg py-1.5 px-2 hover:bg-atmosphere-light focus-within:bg-atmosphere-light"
                :class="selectedNavItem === 2 ? 'bg-atmosphere-light' : ''"
            >
                <button
                    id="2"
                    type="button"
                    class="w-full flex items-center gap-3"
                    @click="handleNavItemClick"
                >
                    <Inbox
                        :size="26"
                        :stroke-width="1.5"
                        color="var(--color-white-base)"
                    />
                    <span class="text-white-base">Inbox</span>
                </button>
            </div>
            <div
                class="rounded-lg py-1.5 px-2 hover:bg-atmosphere-light focus-within:bg-atmosphere-light"
                :class="selectedNavItem === 3 ? 'bg-atmosphere-light' : ''"
            >
                <button
                    id="3"
                    type="button"
                    class="w-full flex items-center gap-3"
                    @click="handleNavItemClick"
                >
                    <NotebookPen
                        :size="26"
                        :stroke-width="1.5"
                        color="var(--color-white-base)"
                    />
                    <span class="text-white-base">Scratchpad</span>
                </button>
            </div>
            <div
                class="rounded-lg py-1.5 px-2 hover:bg-atmosphere-light focus-within:bg-atmosphere-light"
                :class="selectedNavItem === 4 ? 'bg-atmosphere-light' : ''"
            >
                <button
                    id="4"
                    type="button"
                    class="w-full flex items-center gap-3"
                    @click="handleNavItemClick"
                >
                    <ChartLine
                        :size="26"
                        :stroke-width="1.5"
                        color="var(--color-white-base)"
                    />
                    <span class="text-white-base">Analytics</span>
                </button>
            </div>
            <div
                class="rounded-lg mt-auto py-1.5 px-2 hover:bg-atmosphere-light focus-within:bg-atmosphere-light"
                :class="selectedNavItem === 5 ? 'bg-atmosphere-light' : ''"
            >
                <button
                    id="5"
                    type="button"
                    class="w-full flex items-center gap-3"
                    @click="handleNavItemClick"
                >
                    <Settings
                        :size="26"
                        :stroke-width="1.5"
                        color="var(--color-white-base)"
                    />
                    <span class="text-white-base">Settings</span>
                </button>
            </div>
        </nav>
    </div>
</template>

<style scoped>
button:focus,
button:focus-visible {
    outline: none;
    box-shadow: none;
}
</style>
