<script setup lang="ts">
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'
import { ref } from 'vue'
import { ChevronDown } from '@lucide/vue'
import type { HTMLAttributes, Component } from 'vue'

interface DropdownMenuProps {
    text: string
    textColor?: string
    iconOnly?: boolean
    hideChevron?: boolean
    icon?: Component
    iconSize?: number
    iconColor?: string
    iconStrokeWidth?: number
    disabled?: boolean
    class?: HTMLAttributes['class']
    openClass?: HTMLAttributes['class']
}

const buttonVariants = cva(
    'flex items-center gap-3 cursor-pointer'
)

const props = withDefaults(defineProps<DropdownMenuProps>(), {
    iconOnly: false,
    hideChevron: false,
    iconSize: 24,
    iconColor: 'currentColor',
    iconStrokeWidth: 1.5,
    disabled: false,
})

const isOpen = ref<boolean>(false)
const opensUpward = ref<boolean>(false)
const opensRight = ref<boolean>(false)
const trigger = ref<HTMLButtonElement | null>(null)

function toggleDropdown() {
    if (!isOpen.value && trigger.value) {
        const rect = trigger.value.getBoundingClientRect()
        const spaceAbove = rect.top
        const spaceBelow = window.innerHeight - rect.bottom

        const spaceLeft = rect.left
        const spaceRight = window.innerWidth - rect.right

        opensUpward.value = spaceAbove > spaceBelow
        opensRight.value = spaceRight > spaceLeft
    }
    isOpen.value = !isOpen.value
}
</script>

<template>
    <div class="relative inline-block">
        <button
            :aria-label="props.iconOnly ? props.text : undefined"
            :aria-expanded="isOpen"
            :disabled="props.disabled"
            :class="cn(
                buttonVariants(),
                props.class,
                isOpen && props.openClass
            )"
            ref="trigger"
            type="button"
            @click="toggleDropdown"
        >
            <component
                v-if="props.icon"
                :is="props.icon"
                :size="props.iconSize"
                :color="props.iconColor"
                :stroke-width="props.iconStrokeWidth"
                class="shrink-0"
                aria-hidden="true"
            />

            <span
                v-if="!props.iconOnly"
                :style="{ color: props.textColor }"
            >
                {{ props.text }}
            </span>

            <ChevronDown
                v-if="!props.hideChevron"
                :size="props.iconSize"
                :color="props.iconColor && props.iconColor"
                :stroke-width="props.iconStrokeWidth"
                class="ml-auto shrink-0"
                :class="{ 'rotate-180': isOpen }"
                aria-hidden="true"
            />
        </button>

        <div
            v-if="isOpen"
            class="absolute z-50"
            :class="{
                'top-full mt-1': !opensUpward,
                'bottom-full mb-1': opensUpward,
                'left-0': opensRight,
                'right-0': !opensRight,
            }"
        >
            <slot />
        </div>
    </div>
</template>
