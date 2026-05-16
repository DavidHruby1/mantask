<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

type HeadingProps = {
    variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
    color?: 'primary' | 'secondary';
}

const props = withDefaults(defineProps<HeadingProps>(), {
    variant: 'h3',
    color: 'primary',
})

const headingVariants = cva(
    `font-sans font-semibold tracking-normal antialiased`,
    {
        variants: {
            variant: {
                h1: 'text-4xl',
                h2: 'text-3xl',
                h3: 'text-2xl',
                h4: 'text-xl',
                h5: 'text-lg',
                h6: 'text-base',
            },
            color: {
                primary: 'text-white-base',
                secondary: 'text-white-text',
            },
        },
    },
)
</script>

<template>
    <component
        :is="props.variant"
        :class="cn(headingVariants({
            variant: props.variant,
            color: props.color
        }))"
    >
        <slot />
    </component>
</template>
