<script setup lang="ts">
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/utils/cn'

const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'ghost'
    size?: 'sm' | 'md' | 'lg'
    disabled?: boolean
  }>(),
  {
    variant: 'primary',
    size: 'md',
    disabled: false,
  },
)

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-secondary-black disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary:
          'btn-glass rounded-full focus-visible:ring-white-base',
        secondary:
          'bg-white-surface text-white-base hover:bg-white-surface/80 focus-visible:ring-white-base',
        ghost:
          'text-white-muted hover:text-white-base hover:bg-white-surface focus-visible:ring-white-base',
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
  <button :class="cn(buttonVariants({ variant, size }))" :disabled="disabled">
    <slot />
  </button>
</template>
