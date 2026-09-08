<script setup lang="ts">
import { ref, watch } from 'vue'
import { TaskStatus } from '@/interfaces'
import { tasksStore } from '@/stores/tasks'
import type { AllowedStatus, TaskCreate } from '@/interfaces'

const taskStore = tasksStore()

type Props = {
    isOpen: boolean
    addTaskStatus: AllowedStatus | null
}
const props = defineProps<Props>()

const emit = defineEmits<{
    (e: 'close-modal'): void
}>()

const title = ref<string>('')
const status = ref<AllowedStatus>(props.addTaskStatus ?? TaskStatus.BACKLOG)
const errorMessage = ref('')
const statusOptions: Array<{ value: AllowedStatus; label: string }> = [
    { value: TaskStatus.BACKLOG, label: 'Backlog' },
    { value: TaskStatus.TODO, label: 'To do' },
    { value: TaskStatus.IN_PROGRESS, label: 'In progress' },
]

watch(() => props.isOpen, (isOpen) => {
    if (isOpen) {
        status.value = props.addTaskStatus ?? TaskStatus.BACKLOG
        errorMessage.value = ''
    }
})

function getStatusLabel(status: AllowedStatus): string {
    return statusOptions.find((option) => option.value === status)?.label ?? status
}

async function onCreateTask() {
    errorMessage.value = ''
    const payload: TaskCreate = {
        title: title.value.trim(),
        status: status.value,
        should_review: false
    }

    const createdTask = await taskStore.createTask(payload)
    if (!createdTask) {
        errorMessage.value = 'Unable to create task. Please try again.'
        return
    }

    await taskStore.getTasks()

    title.value = ''
    emit('close-modal')
}
</script>

<template>
    <div
        v-if="isOpen"
        class="
            fixed inset-0 z-50 grid place-items-center
            bg-black/40 p-6 backdrop-blur-[1px]
        "
    >
        <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-task-title"
            class="
                h-[420px] w-[480px] bg-gray-400 p-6
            "
        >
            <form
                class="flex h-full flex-col"
                @submit.prevent="onCreateTask"
            >
                <div>
                    <h2 id="add-task-title">Add task</h2>
                </div>

                <div>
                    <div>
                        <label for="task-title">Title</label>
                        <input
                            id="task-title"
                            v-model="title"
                            type="text"
                            name="title"
                            required
                            maxlength="255"
                        />
                    </div>

                    <div>
                        <label for="task-status">Status</label>
                        <select
                            v-if="props.addTaskStatus === null"
                            id="task-status"
                            v-model="status"
                            name="status"
                        >
                            <option
                                v-for="option in statusOptions"
                                :key="option.value"
                                :value="option.value"
                            >
                                {{ option.label }}
                            </option>
                        </select>
                        <span v-else>{{ getStatusLabel(props.addTaskStatus) }}</span>
                    </div>
                </div>

                <p v-if="errorMessage" role="alert">{{ errorMessage }}</p>

                <div class="mt-auto">
                    <button
                        type="button"
                        @click="emit('close-modal')"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                    >
                        Create task
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>
