<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

type LinkProps = {
    href: string;
    color?: 'primary' | 'secondary';
    size: 'xs' | 'sm' | 'md' | 'lg';
}

const props = withDefaults(defineProps<LinkProps>(), {
    color: 'primary',
    size: 'md',
})

const linkVariants = cva(
    `text-white-text font-sans font-normal tracking-normal antialiased
    cursor-pointer transition-colors duration-200 hover:text-white-base`,
    {
        variants: {
            color: {
                primary: 'text-dark-muted',
                secondary: '',
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
