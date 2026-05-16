<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

type LinkProps = {
    href: string;
    color?: 'primary' | 'secondary';
    size: 'sm' | 'md' | 'lg';
}

const props = withDefaults(defineProps<LinkProps>(), {
    color: 'primary',
    size: 'md',
})

const linkVariants = cva(
    `text-white-text font-sans font-normal leading-6 tracking-normal antialiased
    cursor-pointer transition-colors duration-200 hover:text-white-base`,
    {
        variants: {
            color: {
                primary: 'text-white-muted',
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
    <a
        :href="props.href"
        :class="cn(linkVariants({
            color: props.color,
            size: props.size
        }))"
    >
        <slot />
    </a>
</template>
