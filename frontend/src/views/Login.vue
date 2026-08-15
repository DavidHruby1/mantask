<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { RiGoogleFill } from '@remixicon/vue'
import { useAuthStore } from '@/stores/auth'
import { validateEmail, validatePassword } from '@/utils/validation'

import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'

import type { FormErrors, LoginInput } from '@/interfaces'


const authStore = useAuthStore()
const router = useRouter()
const email = ref<string>('')
const password = ref<string>('')
const formErrors = ref<FormErrors>({
    email: '',
    password: '',
})
const isLoggingIn = ref<boolean>(false)


function validateLoginForm(): boolean {
    const results = [
        validateEmail(email.value, formErrors.value),
        validatePassword(password.value, formErrors.value),
    ]

    return results.every(Boolean)
}

async function handleLoginSubmit() {
    if (isLoggingIn.value || !validateLoginForm()) return

    isLoggingIn.value = true

    try {
        const payload: LoginInput = {
            email: email.value.trim(),
            password: password.value,
        }

        const loginSucceeded = await authStore.login(payload)

        if (loginSucceeded) {
            router.push({ name: 'dashboard' })
        }
    } finally {
        isLoggingIn.value = false
    }
}
</script>

<template>
    <div class="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
        <div class="light-aura"></div>
        <div class="light-beam"></div>
        <div class="light-source"></div>

        <form
            class="relative z-10 flex w-full max-w-[380px] flex-col items-center gap-3 bg-transparent"
            novalidate
            @submit.prevent="handleLoginSubmit"
        >
            <img class="mb-4 h-16 w-16" src="/mantask-logo-svg.svg" alt="Mantask" />

            <h3 class="mb-5 font-sans text-2xl font-semibold tracking-normal text-white-base antialiased">
                Sign in to Mantask
            </h3>

            <Input
                v-model="email"
                id="email"
                aria-label="Email address"
                type="email"
                placeholder="Email address"
                :error="formErrors.email"
                @blur="
                    email.trim() === ''
                        ? (formErrors.email = '')
                        : validateEmail(email, formErrors)
                "
            />
            <Input
                v-model="password"
                id="password"
                aria-label="Password"
                type="password"
                placeholder="Password"
                :error="formErrors.password"
                @blur="
                    password === ''
                        ? (formErrors.password = '')
                        : validatePassword(password, formErrors)
                "
            />

            <div class="flex w-full justify-end">
                <RouterLink
                    class="mb-2 -mt-2 cursor-pointer font-sans text-[13px] leading-4.5 font-normal tracking-normal text-dark-muted antialiased transition-colors duration-200 hover:text-white-base"
                    to="/"
                >
                    Forgot password?
                </RouterLink>
            </div>

            <Button
                type="submit"
                variant="glass"
                size="lg"
            >
                {{isLoggingIn ? 'Logging in...' : 'Login'}}
            </Button>

            <div class="flex w-full items-center gap-3 px-1 text-white-muted/35">
                <span class="h-px flex-1 border-t border-dashed border-current"></span>
                <span class="text-sm leading-none">or</span>
                <span class="h-px flex-1 border-t border-dashed border-current"></span>
            </div>

            <Button
                type="button"
                variant="ghost"
                size="lg"
            >
                <RiGoogleFill
                    size="20px"
                    color="rgba(255,255,255,0.58)"
                    class="shrink-0"
                    aria-hidden="true"
                />
                <span>Sign in with Google</span>
            </Button>

            <p class="mt-2 font-sans text-[13px] leading-4.5 font-normal tracking-normal text-white-muted antialiased">
                Don't have an account?
                <RouterLink
                    class="
                        cursor-pointer font-sans text-[13px] leading-4.5 font-normal tracking-normal
                        text-dark-muted antialiased transition-colors duration-200 hover:text-white-base
                    "
                    to="/"
                >
                    Request an invite
                </RouterLink>
            </p>
        </form>
    </div>
</template>

<style scoped>
.light-aura {
    position: absolute;
    top: -60px;
    left: 50%;
    transform: translateX(-50%);
    width: 140vw;
    height: 60vh;
    background: radial-gradient(
        ellipse 48% 80% at 50% 0%,
        rgba(31, 41, 55, 0.58) 0%,
        rgba(31, 41, 55, 0.26) 55%,
        transparent 80%
    );
    filter: blur(55px);
    pointer-events: none;
}

.light-beam {
    position: absolute;
    top: -30px;
    left: 50%;
    transform: translateX(-50%);
    width: 100vw;
    height: 0;
    background: radial-gradient(
        ellipse 35% 100% at 50% 0%,
        rgba(31, 41, 55, 0.92) 0%,
        rgba(31, 41, 55, 0.52) 30%,
        rgba(31, 41, 55, 0.2) 65%,
        transparent 100%
    );
    filter: blur(38px);
    pointer-events: none;
    animation: beamGrow 0.8s ease-out forwards;
    transform-origin: top center;
}

.light-beam::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 30%;
    height: 100%;
    background: radial-gradient(
        ellipse 40% 100% at 50% 0%,
        rgba(31, 41, 55, 0.68) 0%,
        rgba(31, 41, 55, 0.2) 60%,
        transparent 100%
    );
    filter: blur(20px);
}

.light-beam::after {
    content: '';
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 125%;
    height: 105%;
    background: radial-gradient(
        ellipse 45% 100% at 50% 0%,
        rgba(31, 41, 55, 0.26) 0%,
        transparent 75%
    );
    filter: blur(48px);
}

.light-source {
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 90px;
    background: radial-gradient(circle, rgba(31, 41, 55, 0.92) 0%, transparent 70%);
    filter: blur(26px);
    pointer-events: none;
}

@keyframes circleFadeIn {
    0% {
        opacity: 0.1;
    }
    100% {
        opacity: 1;
    }
}

@keyframes beamGrow {
    0% {
        height: 0;
        opacity: 0;
    }
    100% {
        height: 51vh;
        opacity: 1;
    }
}
</style>
