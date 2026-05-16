<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

type ButtonProps = {
    variant: 'primary' | 'secondary' | 'ghost';
    size: 'sm' | 'md' | 'lg';
    disabled?: boolean;
}

const props = withDefaults(defineProps<ButtonProps>(), {
    variant: 'primary',
    size: 'md',
    disabled: false,
})

const buttonVariants = cva(
    `inline-flex items-center justify-center
    rounded-lg font-medium
    transition-all duration-200
    focus-visible:ring-2 focus-visible:ring-offset-2
    focus-visible:ring-offset-secondary-black focus:outline-none
    disabled:pointer-events-none disabled:opacity-50`,
    {
        variants: {
            variant: {
                primary:
                    'btn-glass rounded-full focus-visible:ring-white-base',
                secondary:
                    `bg-white-surface text-white-base
                    hover:bg-white-surface/80 focus-visible:ring-white-base`,
                ghost:
                    `text-white-muted focus-visible:ring-white-base
                    hover:text-white-base hover:bg-white-surface`,
            },
            size: {
                sm: 'h-8 px-3 text-sm',
                md: 'h-10 px-4 text-base',
                lg: 'h-12 px-6 text-lg',
            },
        },
    },
)
</script>

<template>
    <button
        :class="cn(buttonVariants({
            variant: props.variant,
            size: props.size
        }))"
        :disabled="disabled"
    >
        <slot />
    </button>
</template>
