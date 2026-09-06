<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterView } from 'vue-router'
import Sidebar from '@/components/layouts/Sidebar.vue'
import AddTaskModal from '@/components/modals/AddTaskModal.vue'
import type { AllowedStatus } from '@/interfaces'

// Matches the expanded width clamp(10rem, 16vw, 16rem): 10rem / 0.16 = 62.5rem.
const sidebarBreakpoint = window.matchMedia('(min-width: 62.5rem)')
const canExpandSidebar = ref<boolean>(sidebarBreakpoint.matches)
const isUserCollapsed = ref<boolean>(false)
const isSidebarCollapsed = computed<boolean>(() => !canExpandSidebar.value || isUserCollapsed.value)

const isAddTaskModalOpen = ref<boolean>(false)
const addTaskStatus = ref<AllowedStatus | null>(null)

function onAddTask(status: AllowedStatus | null): void {
    addTaskStatus.value = status
    isAddTaskModalOpen.value = true
}

function onCloseAddTaskModal(): void {
    addTaskStatus.value = null
    isAddTaskModalOpen.value = false
}

function updateSidebarState(event: MediaQueryListEvent) {
    canExpandSidebar.value = event.matches
}

function toggleSidebar() {
    if (canExpandSidebar.value) {
        isUserCollapsed.value = !isUserCollapsed.value
    }
}

onMounted(() => {
    sidebarBreakpoint.addEventListener('change', updateSidebarState)
})

onBeforeUnmount(() => {
    sidebarBreakpoint.removeEventListener('change', updateSidebarState)
})
</script>

<template>
    <div class="flex w-full h-dvh p-2">
        <Sidebar
            :collapsed="isSidebarCollapsed"
            :canExpand="canExpandSidebar"
            class="shrink-0 transition-[width] duration-200"
            :class="isSidebarCollapsed ? 'w-12' : 'w-[clamp(10rem,16vw,16rem)]'"
            @toggle-sidebar="toggleSidebar"
            @add-task="onAddTask"
        />

        <main class="flex-1 min-w-0">
            <RouterView @add-task="onAddTask" />
        </main>

        <AddTaskModal
            :isOpen="isAddTaskModalOpen"
            :addTaskStatus="addTaskStatus"
            @close-modal="onCloseAddTaskModal"
        />
    </div>
</template>

<style scoped>
</style>
