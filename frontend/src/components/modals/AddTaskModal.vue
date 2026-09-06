<script setup lang="ts">
type Props = {
    isOpen: boolean
    canSelectStatus: boolean
}
const props = defineProps<Props>()

const emit = defineEmits<{
    (e: 'close-modal'): void
}>()
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
            <form class="flex h-full flex-col">
                <div>
                    <h2 id="add-task-title">Add task</h2>
                </div>

                <div>
                    <div>
                        <label for="task-title">Title</label>
                        <input
                            id="task-title"
                            type="text"
                            name="title"
                            required
                            maxlength="255"
                        />
                    </div>

                    <div>
                        <label for="task-status">Status</label>
                        <select
                            v-if="props.canSelectStatus"
                            id="task-status"
                            name="status"
                        >
                            <option value="backlog">Backlog</option>
                            <option value="todo">To do</option>
                            <option value="in_progress">In progress</option>
                        </select>
                    </div>
                </div>

                <div class="mt-auto">
                    <button type="button" @click="$emit('close-modal')">Cancel</button>
                    <button type="submit">Create task</button>
                </div>
            </form>
        </div>
    </div>
</template>
