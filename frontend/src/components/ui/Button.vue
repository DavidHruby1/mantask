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
                sm: 'w-full h-8 px-3 text-sm',
                md: 'w-full h-10 px-4 text-base',
                lg: 'w-full h-12 px-6 text-lg',
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

<style scoped>
/* Glass button (primary variant) */
.btn-glass {
    position: relative;
    z-index: 1;
    gap: 10px;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-top-color: rgba(255, 255, 255, 0.13);
    background:
        radial-gradient(circle at 22% 38%, rgba(255,255,255,0.06) 0%, transparent 40%),
        radial-gradient(circle at 70% 62%, rgba(255,255,255,0.04) 0%, transparent 45%),
        linear-gradient(160deg, rgba(30,40,58,0.9) 0%, rgba(12,16,24,0.95) 100%);
    -webkit-backdrop-filter: blur(24px) saturate(160%);
    backdrop-filter: blur(24px) saturate(160%);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.1),
        inset 0 -5px 12px rgba(0,0,0,0.4),
        0 4px 18px 2px rgba(0,0,0,0.25);
    color: rgba(255,255,255,0.72);
    text-shadow: 0 1px 3px rgba(0,0,0,0.5);
    cursor: pointer;
    overflow: hidden;
    isolation: isolate;
    transition:
        backdrop-filter 0.4s ease,
        -webkit-backdrop-filter 0.4s ease,
        box-shadow 0.4s ease,
        border-color 0.4s ease,
        color 0.3s ease,
        transform 0.15s ease,
        background 0.4s ease;
}

.btn-glass::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    pointer-events: none;
    background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.05) 22%, transparent 46%);
    opacity: 0.6;
    mix-blend-mode: screen;
}

/* Subtle radial pulse glow behind */
.btn-glass::after {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: inherit;
    background: radial-gradient(circle at 50% 50%, rgba(148, 163, 184, 0.15) 0%, transparent 70%);
    opacity: 0;
    filter: blur(8px);
    transition: opacity 0.45s ease;
    z-index: -1;
    pointer-events: none;
}

.btn-glass:hover {
    color: rgba(255, 255, 255, 0.9);
    border-color: rgba(255, 255, 255, 0.2);
    -webkit-backdrop-filter: blur(32px) saturate(200%);
    backdrop-filter: blur(32px) saturate(200%);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.16),
        inset 0 -5px 12px rgba(0,0,0,0.3),
        0 8px 28px rgba(0,0,0,0.3),
        0 0 0 1px rgba(255,255,255,0.08);
}

.btn-glass:hover::after {
    opacity: 1;
}

.btn-glass:active {
    transform: scale(0.98);
    color: rgba(255,255,255,0.78);
    border-color: rgba(255,255,255,0.15);
    border-top-color: rgba(200, 220, 255, 0.25);
    background:
        radial-gradient(circle at 22% 38%, rgba(255,255,255,0.10) 0%, transparent 40%),
        radial-gradient(circle at 70% 62%, rgba(200,220,255,0.06) 0%, transparent 45%),
        linear-gradient(160deg, rgba(30,40,58,0.96) 0%, rgba(12,16,24,0.98) 100%);
    -webkit-backdrop-filter: blur(18px) saturate(140%);
    backdrop-filter: blur(18px) saturate(140%);
    box-shadow:
        inset 0 2px 10px rgba(0,0,0,0.5),
        inset 0 -3px 8px rgba(0,0,0,0.4),
        0 2px 6px rgba(0,0,0,0.15);
    transition: 50ms ease;
}

.btn-glass:active::before {
    background: linear-gradient(120deg, transparent 0%, rgba(200,220,255,0.08) 22%, transparent 46%);
    opacity: 0.85;
}

.btn-glass:active::after {
    opacity: 0.4;
    background: radial-gradient(circle at 50% 50%, rgba(200, 220, 255, 0.12) 0%, transparent 70%);
}
</style>
