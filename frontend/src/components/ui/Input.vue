<script setup lang="ts">
import { ref, type HTMLAttributes } from 'vue'
import { cva } from 'class-variance-authority'
import { Eye, EyeOff } from '@lucide/vue'
import { cn } from '@/utils/cn'

interface InputProps {
    size?: 'sm' | 'md' | 'lg'
    class?: HTMLAttributes['class']
    type?: 'text' | 'number' | 'email' | 'password'
    placeholder?: string
    disabled?: boolean
    required?: boolean
    error?: string
}

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<InputProps>(), {
    type: 'text',
    disabled: false,
    required: false,
})

const inputModel = defineModel<string>()

const inputVariants = cva(
    `w-full bg-surface-field text-text-secondary
    font-normal outline-none
    border-1 border-border-default rounded-lg
    placeholder:text-text-placeholder placeholder:font-normal
    disabled:pointer-events-none disabled:opacity-50
    focus-visible:bg-surface-field-focus focus-visible:border-border-focus
    focus-visible:placeholder:text-text-placeholder-focus
    transition-[border-color,background] duration-100 ease-in-out
    `,
    {
        variants: {
            size: {
                sm: 'px-2.5 py-2 text-sm',
                md: 'px-3 py-2.5 text-base',
                lg: 'px-4 py-3 text-lg',
            },
            hasPasswordToggle: {
                true: 'pr-10',
                false: null,
            },
        },
        defaultVariants: {
            size: 'md',
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
                        size: props.size,
                        hasPasswordToggle: props.type === 'password',
                    }),
                    props.class,
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
            @pointerdown.prevent
            @click="togglePasswordVisibility"
        >
            <Eye
                v-if="isPasswordVisible"
                :size="20"
                :stroke-width="1.25"
                color="rgba(255,255,255,0.58)"
                class="shrink-0"
                aria-hidden="true"
            />
            <EyeOff
                v-else
                :size="20"
                :stroke-width="1.25"
                color="rgba(255,255,255,0.58)"
                class="shrink-0"
                aria-hidden="true"
            />
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
    -webkit-text-fill-color: var(--color-text-secondary);
    caret-color: var(--color-text-secondary);
    box-shadow: 0 0 0 1000px var(--color-surface-field) inset;
    transition: background-color 9999s ease-out;
}
</style>
