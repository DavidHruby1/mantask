<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

type TextProps = {
    color?: 'primary' | 'secondary';
    size: 'sm' | 'md' | 'lg';
}

const props = withDefaults(defineProps<TextProps>(), {
    color: 'primary',
    size: 'md',
})

const textVariants = cva(
    `text-white-text font-sans font-normal leading-6 tracking-normal antialiased`,
    {
        variants: {
            color: {
                primary: '',
                secondary: '',
            },
            size: {
                sm: '',
                md: '',
                lg: '',
            },
        },
    },
)
</script>

<template>
    <p
        :class="cn(textVariants({
            color: props.color,
            size: props.size
        }))"
    >
        <slot />
    </p>
</template>
