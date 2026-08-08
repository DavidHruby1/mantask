<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

type FormProps = {
    variant?: 'transparent' | 'card'
    loading?: boolean
    novalidate?: boolean
}

const props = withDefaults(defineProps<FormProps>(), {
    loading: false,
    novalidate: false,
})

const emit = defineEmits<{
    'submit-form': [event: Event]
}>()

const formVariants = cva(`flex flex-col items-center gap-3 relative z-10`, {
    variants: {
        variant: {
            transparent: 'bg-transparent max-w-[380px] w-full',
            card: `box-content w-[calc(100%_-_80px)] min-w-[240px] max-w-[380px] p-10
                rounded-[24px] border border-white-surface bg-secondary-black [&>button]:mt-2`,
        },
    },
})

function handleSubmit(event: Event) {
    if (props.loading) {
        return
    }
    emit('submit-form', event)
}
</script>

<template>
    <form
        :class="cn(formVariants({ variant: props.variant }))"
        :novalidate="props.novalidate"
        :aria-busy="props.loading"
        @submit.prevent="handleSubmit"
    >
        <slot />
    </form>
</template>
