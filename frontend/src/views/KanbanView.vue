<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { tasksStore } from '@/stores/tasks'
import { TaskStatus } from '@/interfaces'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import {
    CirclePlus,
    Ellipsis,
    ListSortDescending,
    Funnel,
    MoveUp,
    MoveDown,
} from '@lucide/vue'
import type { AllowedStatus } from '@/interfaces'

const emit = defineEmits<{
    (e: 'add-task', status: AllowedStatus): void
}>()

const taskStore = tasksStore()
const { tasks } = storeToRefs(taskStore)

const isSortAscending = ref<boolean>(true)

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

</script>

<template>
    <div class="box-border overflow-hidden flex flex-col min-h-0 h-full pl-2">
        <!-- KanbanControls -->
        <div>
            <div class="flex justify-between items-center px-3 py-1 text-white-base">
                <div>
                    <span>Selected Layers</span>
                </div>


                <div class="flex justify-center items-center gap-2">
                    <input class="bg-gray-300 mr-6 min-w-80 p-1 rounded-lg"/>

                    <DropdownMenu
                        text="Sort"
                        :icon="ListSortDescending"
                        :icon-only="true"
                        :icon-stroke-width="2"
                        :hide-chevron="true"
                    >
                        <li class="text-white-base">Priority</li>
                        <li class="text-white-base">Effort</li>
                        <li class="text-white-base">Due date</li>
                        <li class="text-white-base">Review date</li>
                    </DropdownMenu>

                    <button
                        type="button"
                        @click="isSortAscending = !isSortAscending"
                    >
                        <MoveUp
                            v-if="isSortAscending"
                            :size="24"
                            :stroke-width="2"
                            class="shrink-0 cursor-pointer"
                        />
                        <MoveDown
                            v-else
                            :size="24"
                            :stroke-width="2"
                            class="shrink-0 cursor-pointer"
                        />
                    </button>

                    <button
                        type="button"
                    >
                        <Funnel
                            :size="24"
                            :stroke-width="2"
                            class="shrink-0 cursor-pointer"
                        />
                    </button>
                </div>
            </div>

            <div
                class="flex justify-start items-center gap-3 rounded-lg bg-zinc-900 p-3 mt-2 text-white-base"
            >
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
                <div class="flex justify-between items-center px-1">
                    <span class="text-lg">{{ column.label }}</span>

                    <div class="flex gap-2">
                        <button
                            v-if="isAllowedTaskStatus(column.status)"
                            type="button"
                            @click="addTask(column.status)"
                        >
                            <CirclePlus
                                :size="20"
                                :stroke-width="1.5"
                                color="var(--color-white-base)"
                                class="shrink-0 cursor-pointer"
                            />
                        </button>

                        <button
                            type="button"
                        >
                            <Ellipsis
                                :size="20"
                                :stroke-width="1.5"
                                color="var(--color-white-base)"
                                class="shrink-0 cursor-pointer"
                            />
                        </button>
                    </div>
                </div>

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
