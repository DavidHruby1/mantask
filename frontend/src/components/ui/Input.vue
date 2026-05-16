<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

type InputProps = {
    variant?: 'underlined' | 'outlined';
    size: 'sm' | 'md' | 'lg';
    type: 'text' | 'number' | 'email' | 'password';
    placeholder?: string;
    disabled?: boolean;
    required?: boolean;
}

const props = withDefaults(defineProps<InputProps>(), {
    size: 'md',
    type: 'text',
    disabled: false,
    required: false,
})

const inputVariants = cva(
    `bg-dark-surface text-white-text
    font-normal outline-none
    border-1 border-white-surface rounded-lg
    placeholder:text-white-placeholder placeholder:font-normal
    disabled:pointer-events-none disabled:opacity-50
    focus-visible:bg-dark-surface-focus focus-visible:border-white-surface-focus
    focus-visible:placeholder:text-white-placeholder-focus
    transition-[border-color,background] duration-100 ease-in-out
    `,
    {
        variants: {
            variant: {
                underlined:
                    '',
                outlined:
                    '',
            },
            size: {
                sm: 'w-full text-sm',
                md: 'w-full text-base px-3 py-[10px]',
                lg: 'w-full text-lg',
            },
        },
    },
)
</script>

<template>
    <input
        :type="props.type"
        :class="cn(inputVariants({
            variant: props.variant,
            size: props.size
        }))"
        :placeholder="props.placeholder"
        :disabled="props.disabled"
        :required="props.required"
    />
</template>

