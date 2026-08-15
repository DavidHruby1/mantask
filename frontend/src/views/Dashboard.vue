<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { tasksStore } from '@/stores/tasks'

import type { TaskStatus, TaskCreate, TaskRead } from '@/interfaces'

const taskStore = tasksStore()


onMounted(() => {
    void taskStore.getTasks()
})
</script>

<template>
</template>

<style scoped>
</style>

