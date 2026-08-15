<script setup lang="ts">
import { ref, type HTMLAttributes } from 'vue'
import { cva } from 'class-variance-authority'
import { RiEyeLine, RiEyeOffLine } from '@remixicon/vue'
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
    `w-full bg-input-black text-white-text
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
            <RiEyeLine
                v-if="isPasswordVisible"
                size="20px"
                color="rgba(255,255,255,0.58)"
                class="shrink-0"
                aria-hidden="true"
            />
            <RiEyeOffLine
                v-else
                size="20px"
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
    -webkit-text-fill-color: var(--color-white-text);
    caret-color: var(--color-white-text);
    box-shadow: 0 0 0 1000px var(--color-input-black) inset;
    transition: background-color 9999s ease-out;
}
</style>
