<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { tasksStore } from '@/stores/tasks'
import { TaskStatus } from '@/interfaces'
import type { AllowedStatus } from '@/interfaces'

const emit = defineEmits<{
    (e: 'add-task', status: AllowedStatus): void
}>()

const taskStore = tasksStore()
const { tasks } = storeToRefs(taskStore)

const statusColumns = [
    { status: TaskStatus.BACKLOG, label: 'Backlog' },
    { status: TaskStatus.TODO, label: 'To do' },
    { status: TaskStatus.IN_PROGRESS, label: 'In progress' },
    { status: TaskStatus.REVIEW, label: 'Review' },
    { status: TaskStatus.DONE, label: 'Done' },
] as const

function isAllowedTaskStatus(status: TaskStatus): status is AllowedStatus {
    return status !== TaskStatus.REVIEW && status !== TaskStatus.DONE
}

function addTask(status: TaskStatus): void {
    if (!isAllowedTaskStatus(status)) {
        return
    }

    emit('add-task', status)
}

onMounted(async () => {
    const tasksLog = await taskStore.getTasks()
    console.log('Fetched tasks:', tasksLog)
})

// Get tasks and separate them into status columns
</script>

<template>
    <div class="box-border overflow-hidden flex flex-col min-h-0 h-full pl-2">
        <!-- KanbanControls -->
        <div>
            <div class="flex justify-between items-center bg-white p-4">
                <div>
                    <span>Selected Layers</span>
                </div>

                <div class="flex gap-3">
                    <input class="bg-gray-300"/>
                    <button type="button">Sort</button>
                    <button type="button">Filter</button>
                </div>
            </div>

            <div class="flex justify-start items-center gap-3 bg-white p-4 mt-2">
                <button type="button">Layers</button>
                <button type="button">My tasks</button>
            </div>
        </div>

        <!-- KanbanBoard -->
        <div class="kanban">
            <div
                v-for="column in statusColumns" :key="column.status"
                class="bg-zinc-900 rounded-lg p-2"
            >
                <span>{{ column.label }}</span>
                <button
                    v-if="isAllowedTaskStatus(column.status)"
                    type="button"
                    @click="addTask(column.status)"
                >
                    +
                </button>

                <template v-for="task in tasks" :key="task.id">
                    <div v-if="task.status === column.status">
                        <span>{{ task.title }}</span>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>

<style scoped>
.kanban {
    display: flex;
    min-height: 0;
    flex: 1;
    gap: 0.75rem;
    margin-top: 0.5rem;
    overflow-x: auto;
    color: white;
}

.kanban > div {
    flex: 0 0 clamp(240px, 28vw, 340px);
}
</style>
