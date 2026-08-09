<script setup lang="ts">
import { computed, useAttrs } from 'vue'
import { cn } from '@/utils/cn'

defineOptions({
    inheritAttrs: false,
})

const attrs = useAttrs()

const forwardedAttrs = computed(() => {
    const rest = { ...attrs }
    delete rest.class
    return rest
})

</script>

<template>
    <div
        v-bind="forwardedAttrs"
        :class="cn('relative flex min-h-screen items-center justify-center overflow-hidden px-4', attrs.class as string)"
    >
        <slot />
    </div>
</template>
