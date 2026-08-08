<script setup lang="ts">
import { ref } from 'vue'
import { cva } from 'class-variance-authority'
import { cn } from '@/utils/cn'

import type { InputProps } from '@/interfaces'

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<InputProps>(), {
    size: 'md',
    type: 'text',
    disabled: false,
    required: false,
})

const inputModel = defineModel<string>()

const inputVariants = cva(
    `bg-input-black text-white-text
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
                underlined: '',
                outlined: '',
            },
            size: {
                sm: 'w-full text-sm',
                md: 'w-full text-base px-3 py-[10px]',
                lg: 'w-full text-lg',
            },
        },
    },
)

const inputType = ref(props.type)
const isPasswordVisible = ref(false)

const togglePasswordVisibility = () => {
    isPasswordVisible.value = !isPasswordVisible.value
    inputType.value = isPasswordVisible.value ? 'text' : 'password'
}
</script>

<template>
    <span class="relative w-full">
        <input
            v-model="inputModel"
            v-bind="$attrs"
            :type="inputType"
            :class="
                cn(
                    inputVariants({
                        variant: props.variant,
                        size: props.size,
                    }),
                    { 'pr-10' : props.type === 'password' }
                )
            "
            :placeholder="props.placeholder"
            :disabled="props.disabled"
            :required="props.required"
            :aria-invalid="Boolean(props.error)"
        />
        <button
            v-if="props.type === 'password'"
            :aria-label="isPasswordVisible ? 'Hide password' : 'Show password'"
            type='button'
            class="absolute right-4 top-1/2 -translate-y-1/2 cursor-pointer"
            @click="togglePasswordVisibility"
        >
            <img
                :src="isPasswordVisible ? '/eye-line.svg' : '/eye-off-line.svg'"
                class="h-5 w-5 shrink-0"
                alt=""
            >
        </button>
        <p v-if="props.error" class="w-full text-sm text-red-700">
            {{ props.error }}
        </p>
    </span>
</template>

<style scoped>
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
    -webkit-text-fill-color: var(--color-white-text);
    caret-color: var(--color-white-text);
    box-shadow: 0 0 0 1000px var(--color-input-black) inset;
    transition: background-color 9999s ease-out;
}
</style>
