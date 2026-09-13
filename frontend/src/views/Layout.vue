<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { RouterView } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'
import AddTaskModal from '@/components/modals/AddTaskModal.vue'
import { useTeamsStore } from '@/stores/teams'
import type { AllowedStatus } from '@/interfaces'

// Matches the expanded width clamp(10rem, 16vw, 16rem): 10rem / 0.16 = 62.5rem.
const sidebarBreakpoint = window.matchMedia('(min-width: 62.5rem)')
const canExpandSidebar = ref<boolean>(sidebarBreakpoint.matches)
const isUserCollapsed = ref<boolean>(false)
const isSidebarCollapsed = computed<boolean>(() => !canExpandSidebar.value || isUserCollapsed.value)

const isAddTaskModalOpen = ref<boolean>(false)
const addTaskStatus = ref<AllowedStatus | null>(null)
const addTaskTeamId = ref<number | null>(null)
const teamsStore = useTeamsStore()
const { selectedTeamId } = storeToRefs(teamsStore)

function onAddTask(status: AllowedStatus | null): void {
    if (selectedTeamId.value === null) return

    addTaskStatus.value = status
    addTaskTeamId.value = selectedTeamId.value
    isAddTaskModalOpen.value = true
}

function onCloseAddTaskModal(): void {
    addTaskStatus.value = null
    addTaskTeamId.value = null
    isAddTaskModalOpen.value = false
}

watch(selectedTeamId, () => {
    onCloseAddTaskModal()
})

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
            v-if="addTaskTeamId !== null"
            :isOpen="isAddTaskModalOpen"
            :addTaskStatus="addTaskStatus"
            :teamId="addTaskTeamId"
            @close-modal="onCloseAddTaskModal"
        />
    </div>
</template>

<style scoped>
</style>
