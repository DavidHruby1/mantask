<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { RouterView } from 'vue-router'
import Sidebar from '@/components/layouts/Sidebar.vue'

const largeBreakpoint = window.matchMedia('(min-width: 64rem)') // 1024x
const isSidebarCollapsed = ref(!largeBreakpoint.matches)

function updateSidebarState(event: MediaQueryListEvent) {
    isSidebarCollapsed.value = !event.matches
}

onMounted(() => {
    largeBreakpoint.addEventListener('change', updateSidebarState)
})

onBeforeUnmount(() => {
    largeBreakpoint.removeEventListener('change', updateSidebarState)
})
</script>

<template>
    <div class="flex w-full h-dvh p-2">
        <Sidebar
            :collapsed="isSidebarCollapsed"
            class="shrink-0 transition-[width] duration-200"
            :class="isSidebarCollapsed ? 'w-12' : 'w-[clamp(4rem,16vw,16rem)]'"
            @toggle-sidebar="isSidebarCollapsed = !isSidebarCollapsed"
        />

        <main class="flex-1 min-w-0">
            <RouterView />
        </main>
    </div>
</template>

<style scoped>
</style>
