<script setup lang="ts">
import { computed, useAttrs } from 'vue'
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

defineOptions({
    inheritAttrs: false,
})

const attrs = useAttrs()

const forwardedAttrs = computed(() => {
    const { class: _class, ...rest } = attrs
    return rest
})

const containerVariants = cva(
    `relative min-h-screen flex items-center justify-center overflow-hidden px-4`,
)
</script>

<template>
    <div
        v-bind="forwardedAttrs"
        :class="cn(containerVariants(), attrs.class as string)"
    >
        <slot />
    </div>
</template>
