<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { RouterLink } from 'vue-router'
import { cn } from '@/utils/cn'

import type { LinkProps } from '@/interfaces'

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
    <RouterLink
        :to="props.to"
        :class="
            cn(
                linkVariants({
                    color: props.color,
                    size: props.size,
                }),
            )
        "
    >
        <slot />
    </RouterLink>
</template>
