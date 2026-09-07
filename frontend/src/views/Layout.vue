<script setup lang="ts">
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'

const isSidebarCollapsed = ref(false)
</script>

<template>
    <div class="flex w-full h-dvh p-1">
        <Sidebar
            :collapsed="isSidebarCollapsed"
            class="shrink-0 transition-[width] duration-200"
            :class="isSidebarCollapsed ? 'w-12' : 'w-64'"
            @toggle-sidebar="isSidebarCollapsed = !isSidebarCollapsed"
        />

        <main class="flex-1 min-w-0">
            <RouterView />
        </main>
    </div>
</template>

<style scoped>
</style>
