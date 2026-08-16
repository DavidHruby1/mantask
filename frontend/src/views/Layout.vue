<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterView } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'


onMounted(() => {
})
//
</script>

<template>
    <div class="flex w-full h-dvh p-1">
        <Sidebar class="flex-[1_1_0%]"/>

        <main class="flex-[5_1_0%]">
            <RouterView />
        </main>
    </div>
</template>

<style scoped>
</style>
