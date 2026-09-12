<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { tasksStore } from '@/stores/tasks'
import { TaskStatus, TaskPriority } from '@/interfaces'
import DropdownMenu from '@/components/ui/DropdownMenu.vue'
import {
    CirclePlus,
    Ellipsis,
    ListSortDescending,
    Funnel,
    MoveUp,
    MoveDown,
    Search
} from '@lucide/vue'
import type { TaskRead, AllowedStatus } from '@/interfaces'

const emit = defineEmits<{
    (e: 'add-task', status: AllowedStatus): void
}>()

type SortKey = 'manual' | 'priority' | 'effort' | 'due_date' | 'review_date' | 'created_at'

const taskStore = tasksStore()
const { tasks } = storeToRefs(taskStore)

const sortKey = ref<SortKey>('manual')
const isSortAscending = ref<boolean>(true)
const searchQuery = ref<string>('')

const statusColumns: Array<{ status: TaskStatus; label: string }> = [
    { status: TaskStatus.BACKLOG, label: 'Backlog' },
    { status: TaskStatus.TODO, label: 'To do' },
    { status: TaskStatus.IN_PROGRESS, label: 'In progress' },
    { status: TaskStatus.REVIEW, label: 'Review' },
    { status: TaskStatus.DONE, label: 'Done' },
] as const

const priorityRank: Record<TaskPriority, number> = {
    [TaskPriority.LOW]: 1,
    [TaskPriority.MEDIUM]: 2,
    [TaskPriority.HIGH]: 3,
    [TaskPriority.URGENT]: 4,
} as const

const sortOptions: Array<{ value: SortKey; label: string }> = [
    { value: 'manual', label: 'Manual' },
    { value: 'priority', label: 'Priority' },
    { value: 'effort', label: 'Effort' },
    { value: 'due_date', label: 'Due date' },
    { value: 'created_at', label: 'Created at' },
    { value: 'review_date', label: 'Review date' },
] as const

// When the component is mounted, try to restore sorting from local storage
try {
    const savedSortKey = localStorage.getItem('kanban.sortKey')
    sortKey.value = sortOptions.find(option => option.value === savedSortKey)?.value ?? 'manual'
    isSortAscending.value = localStorage.getItem('kanban.isSortAscending') !== 'false'
} catch (error) {
    console.warn('Could not restore Kanban sorting:', error)
}

// Watches for changes in sortKey and isSortAscending and saves them to local storage on change
watch([sortKey, isSortAscending], ([key, ascending]) => {
    try {
        localStorage.setItem('kanban.sortKey', key)
        localStorage.setItem('kanban.isSortAscending', String(ascending))
    } catch (error) {
        console.warn('Could not save Kanban sorting:', error)
    }
})

// Used for sorting
const tasksToRender = computed<TaskRead[]>(() => {
    // Returning [...tasks.value] to avoid mutating the original array
    return [...tasks.value]
        .filter(task => task.title.toLowerCase().includes(searchQuery.value.toLowerCase()))
        .sort((a, b): number => {
        switch (sortKey.value) {
            case 'manual':
                return 0

            case 'priority':
                if (a.priority == null || b.priority == null) {
                    return 0
                }
                return isSortAscending.value
                    ? priorityRank[a.priority] - priorityRank[b.priority]
                    : priorityRank[b.priority] - priorityRank[a.priority]

            case 'effort':
                if (a.effort == null || b.effort == null) {
                    return 0
                }
                return isSortAscending.value
                    ? a.effort - b.effort
                    : b.effort - a.effort

            case 'due_date':
            case 'review_date':
            case 'created_at': {
                const dateA = a[sortKey.value]
                const dateB = b[sortKey.value]

                if (dateA == null || dateB == null) {
                    return 0
                }

                return isSortAscending.value
                    ? new Date(dateA).getTime() - new Date(dateB).getTime()
                    : new Date(dateB).getTime() - new Date(dateA).getTime()
            }

            default:
                return 0
        }
    })
})

function onSortChange(key: SortKey): void {
    sortKey.value = key
}

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
                    <div class="relative">
                        <input
                            v-model="searchQuery"
                            class="
                                bg-gray-200 mr-6 min-w-80 p-1 rounded-lg outline-none border-none
                                placeholder:text-dark-surface-active/60 text-accent-black pl-2 pr-8
                            "
                            type="text"
                            placeholder="Search tasks here..."
                        />
                        <Search
                            :size="22"
                            :stroke-width="1.75"
                            color="var(--color-dark-surface-active)"
                            class="
                                absolute right-8 top-1/2 -translate-y-1/2 shrink-0
                                cursor-pointer opacity-60
                            "
                        />
                    </div>

                    <DropdownMenu
                        text="Sort"
                        :icon="ListSortDescending"
                        :icon-only="true"
                        :icon-stroke-width="2"
                        :hide-chevron="true"
                    >
                        <li
                            v-for="option in sortOptions"
                            :key="option.value"
                            :class="option.value === sortKey ? 'bg-dark-surface-active' : ''"
                            class="text-white-base"
                        >
                            <button
                                type="button"
                                class="w-full text-left"
                                @click="onSortChange(option.value)"
                            >
                                {{ option.label }}
                            </button>
                        </li>
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

                <template v-for="task in tasksToRender" :key="task.id">
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
