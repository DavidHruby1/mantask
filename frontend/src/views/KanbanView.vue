<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { tasksStore } from '@/stores/tasks'
import { TaskStatus } from '@/interfaces'

const taskStore = tasksStore()
const { tasks, isLoadingTasks } = storeToRefs(taskStore)
const emit = defineEmits<{
    (e: 'add-task', status: TaskStatus.BACKLOG): void
}>()
const statusColumns: Record<string, string> = {
    backlog: 'Backlog',
    todo: 'To do',
    in_progress: 'In progress',
    review: 'Review',
    done: 'Done'
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
        <div class="kanban bg-white">
            <div v-for="status in Object.keys(statusColumns)" :key="status">
                <span>{{ statusColumns[status] }}</span>
                <button
                    v-if="status === TaskStatus.BACKLOG"
                    type="button"
                    @click="emit('add-task', TaskStatus.BACKLOG)"
                >
                    +
                </button>
                <div v-for="task in tasks" :key="task.id">
                    <span>{{ task.status === status ? task.title : undefined }}</span>
                </div>
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
