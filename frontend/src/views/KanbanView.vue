<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { tasksStore } from '@/stores/tasks'
import { TaskStatus } from '@/interfaces'

const taskStore = tasksStore()
const { tasks } = storeToRefs(taskStore)

const statusColumns = [
    { status: TaskStatus.BACKLOG, label: 'Backlog' },
    { status: TaskStatus.TODO, label: 'To do' },
    { status: TaskStatus.IN_PROGRESS, label: 'In progress' },
    { status: TaskStatus.REVIEW, label: 'Review' },
    { status: TaskStatus.DONE, label: 'Done' },
] as const

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
        <div class="kanban bg-white">
            <div v-for="column in statusColumns" :key="column.status">
                <span>{{ column.label }}</span>
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
    gap: 12px;
    margin-top: 0.5rem;
    overflow-x: auto;
}

.kanban > div {
    flex: 0 0 clamp(240px, 28vw, 340px);
    background: red;
}
</style>
