<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

type TextProps = {
    color?: 'primary' | 'secondary';
    size: 'xs' | 'sm' | 'md' | 'lg';
}

const props = withDefaults(defineProps<TextProps>(), {
    color: 'primary',
    size: 'md',
})

const textVariants = cva(
    `text-white-text font-sans font-normal tracking-normal antialiased`,
    {
        variants: {
            color: {
                primary: '',
                secondary: 'text-white-muted',
            },
            size: {
                xs: 'text-[13px] leading-[18px]',
                sm: 'text-sm leading-5',
                md: 'text-base leading-6',
                lg: 'text-lg leading-7',
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
