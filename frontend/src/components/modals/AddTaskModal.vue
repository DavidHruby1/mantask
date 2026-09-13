<script setup lang="ts">
import { ref, watch } from 'vue'
import { TaskStatus } from '@/interfaces'
import { tasksStore } from '@/stores/tasks'
import { useTeamsStore } from '@/stores/teams'
import { storeToRefs } from 'pinia'
import type { AllowedStatus, TaskCreate } from '@/interfaces'

const taskStore = tasksStore()
const teamsStore = useTeamsStore()
const { selectedTeamId } = storeToRefs(teamsStore)

type Props = {
    isOpen: boolean
    addTaskStatus: AllowedStatus | null
    teamId: number
}
const props = defineProps<Props>()

const emit = defineEmits<{
    (e: 'close-modal'): void
}>()

const title = ref<string>('')
const status = ref<AllowedStatus>(props.addTaskStatus ?? TaskStatus.BACKLOG)
const isSubmitting = ref<boolean>(false)
const statusOptions: Array<{ value: AllowedStatus; label: string }> = [
    { value: TaskStatus.BACKLOG, label: 'Backlog' },
    { value: TaskStatus.TODO, label: 'To do' },
    { value: TaskStatus.IN_PROGRESS, label: 'In progress' },
] as const

watch(() => props.isOpen, (isOpen) => {
    if (isOpen) {
        status.value = props.addTaskStatus ?? TaskStatus.BACKLOG
    }
})

function getStatusLabel(status: AllowedStatus): string {
    return statusOptions.find((option) => option.value === status)?.label ?? status
}

async function onCreateTask() {
    if (isSubmitting.value) return

    isSubmitting.value = true
    const submittedTeamId = props.teamId
    const payload: TaskCreate = {
        team_id: submittedTeamId,
        title: title.value.trim(),
        status: status.value,
        should_review: false
    }

    emit('close-modal')
    const createdTask = await taskStore.createTask(payload)
    if (!createdTask) return

    if (selectedTeamId.value === submittedTeamId) {
        await taskStore.getTasks(submittedTeamId)
    }
}

</script>

<template>
    <div
        role="overlay"
        v-if="isOpen"
        class="fixed inset-0 z-100 grid place-items-center backdrop-blur-xs"
    >
        <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-task-title"
            class="h-105 w-120 bg-surface-raised border border-border-raised p-2 rounded-lg"
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

                <div class="mt-auto">
                    <button
                        type="button"
                        @click="emit('close-modal')"
                    >
                        Cancel
                    </button>
                    <button
                        type="submit"
                        :disabled="isSubmitting"
                    >
                        Create task
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>
