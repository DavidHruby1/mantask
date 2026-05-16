<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

type FormProps = {
    variant?: 'transparent';
    loading?: boolean;
    novalidate?: boolean;
}

const props = withDefaults(defineProps<FormProps>(), {
    loading: false,
    novalidate: false,
})

const emit = defineEmits<{
    submit: [event: Event];
}>()

const formVariants = cva(
    `flex flex-col items-center gap-3 relative z-10`,
    {
        variants: {
            variant: {
                transparent: 'bg-transparent max-w-[340px] w-full',
            },
        },
    },
)

function handleSubmit(event: Event) {
    if (props.loading) {
        return
    }
    emit('submit', event)
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
