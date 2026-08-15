<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
    RiSortDesc,
    RiFilterLine,
    RiSearch2Line,
    RiSwitchLine,
    RiDropdownList
} from '@remixicon/vue'
import { tasksStore } from '@/stores/tasks'


const taskStore = tasksStore()


onMounted(() => {
    void taskStore.getTasks()
})
</script>

<template>
    <div class="flex w-full min-h-dvh p-1">
        <aside class="flex-[1_1_0%] bg-purple-400">
        <!--
            <UserProfile />
            <TeamSwitcher />
            <NavMenu />
        -->
        </aside>

        <main class="flex-[4_1_0%] bg-amber-400">
            <div class="flex justify-between items-center px-1 bg-rose-400">
                <div class="relative flex items-center">
                    <input class="bg-white"/>
                    <button class="absolute right-0 z-10">
                        <RiSearch2Line />
                    </button>
                </div>

                <div class="flex items-center gap-2">
                    <button>
                        <RiSortDesc />
                    </button>

                    <button>
                        <RiFilterLine />
                    </button>
                </div>
            </div>

            <div class="flex flex-col bg-cyan-300 mt-32">
                <div class="flex items-center gap-2 px-2">
                    <button>
                        <RiSwitchLine />
                    </button>

                    <button>
                        <RiDropdownList />
                    </button>
                </div>

                <!-- Kanban board -->
                <div class="h-140 bg-emerald-600 px-2"></div>
            </div>
        </main>

        <div class="hidden"></div>
    </div>
</template>

<style scoped>
</style>
