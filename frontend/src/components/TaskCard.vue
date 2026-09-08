<script setup lang="ts">
import { CalendarClock } from '@lucide/vue'
import type { TaskRead } from '@/interfaces'

type Props = {
    task: TaskRead
}

defineProps<Props>()
</script>

<template>
    <div>
        <h3>{{ task.title }}</h3>

        <!-- Maybe v-for with many layers -->
        <div>
            <span>{{ task.layer }}</span>
        </div

        <div>
            <div><span>{{ task.priority }}</span></div>
            <span>{{ task.effort }}</span>
        </div>

        <div>
            <CalendarClock
                :size="16"
                :stroke-width="1.25"
                color="var(--color-white-base)"
                class="shrink-0"
            />
            <span>{{ task.due_date }}</span>
            <span>{{ task.review_date }}</span>
        </div>

        <div>
            <!-- Avatar -->
            <!-- Username -->
            <!-- Attachments -->
            <!-- Comments -->
        </div>
    </div>
</template>
