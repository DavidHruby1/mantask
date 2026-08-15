<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
    validateBootstrapSecret,
    validateEmail,
    validateOrganizationOrTeamName,
    validatePassword,
    validateUsername,
} from '@/utils/validation'

import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'

import type { BootstrapSetup, FormErrors } from '@/interfaces'


const authStore = useAuthStore()
const router = useRouter()
const username = ref<string>('')
const email = ref<string>('')
const password = ref<string>('')
const organization = ref<string>('')
const team = ref<string>('')
const bootstrapSecret = ref<string>('')
const formErrors = ref<FormErrors>({
    username: '',
    email: '',
    password: '',
    organization: '',
    team: '',
    bootstrapSecret: '',
})
const isSubmitting = ref(false)


function validateBootstrapForm(): boolean {
    const results = [
        validateUsername(username.value, formErrors.value),
        validateEmail(email.value, formErrors.value),
        validatePassword(password.value, formErrors.value),
        validateOrganizationOrTeamName(
            organization.value,
            'organization',
            formErrors.value,
        ),
        validateOrganizationOrTeamName(
            team.value,
            'team',
            formErrors.value,
        ),
        validateBootstrapSecret(bootstrapSecret.value, formErrors.value),
    ]

    return results.every(Boolean)
}

// Submits the validated bootstrap form and navigates to the dashboard after the server creates the account.
async function handleBootstrapSubmit() {
    if (isSubmitting.value || !validateBootstrapForm()) return

    isSubmitting.value = true

    try {
        const payload: BootstrapSetup = {
            username: username.value.trim(),
            email: email.value.trim(),
            password: password.value,
            organization_name: organization.value.trim(),
            team_name: team.value.trim(),
            bootstrap_secret: bootstrapSecret.value,
        }

        const bootstrapSucceeded = await authStore.bootstrap(payload)

        if (bootstrapSucceeded) {
            await router.push({ name: 'dashboard' })
        }
    } finally {
        isSubmitting.value = false
    }
}
</script>

<template>
    <div class="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
        <div class="bootstrap-light-aura"></div>
        <div class="bootstrap-light-source"></div>

        <form
            class="relative z-10 box-content flex w-[calc(100%_-_80px)] min-w-[240px] max-w-[380px] flex-col items-center gap-3 rounded-[24px] border border-white-surface bg-secondary-black p-10 [&>button]:mt-2"
            :aria-busy="isSubmitting"
            @submit.prevent="handleBootstrapSubmit"
        >
            <h3 class="mb-0 font-sans text-2xl font-semibold tracking-normal text-white-base antialiased">
                Set up Mantask
            </h3>

            <p class="mb-5 text-center font-sans text-sm leading-5 font-normal tracking-normal text-white-muted antialiased">
                Claim this Mantask instance and become owner.
            </p>

            <Input
                v-model="username"
                id="username"
                aria-label="Username"
                type="text"
                placeholder="Username"
                :error="formErrors.username"
                @blur="
                    username.trim() === ''
                        ? (formErrors.username = '')
                        : validateUsername(username, formErrors)
                "
            />
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
            <Input
                v-model="organization"
                id="organization-name"
                aria-label="Organization name"
                type="text"
                placeholder="Organization name"
                :error="formErrors.organization"
                @blur="
                    organization.trim() === ''
                        ? (formErrors.organization = '')
                        : validateOrganizationOrTeamName(organization, 'organization', formErrors)
                "
            />
            <Input
                v-model="team"
                id="team-name"
                aria-label="Team name"
                type="text"
                placeholder="Team name"
                :error="formErrors.team"
                @blur="
                    team.trim() === ''
                        ? (formErrors.team = '')
                        : validateOrganizationOrTeamName(team, 'team', formErrors)
                "
            />
            <Input
                v-model="bootstrapSecret"
                id="bootstrap-secret"
                aria-label="Bootstrap secret"
                type="password"
                placeholder="Bootstrap secret"
                :error="formErrors.bootstrapSecret"
                @blur="
                    bootstrapSecret === ''
                        ? (formErrors.bootstrapSecret = '')
                        : validateBootstrapSecret(bootstrapSecret, formErrors)
                "
            />

            <Button
                type="submit"
                variant="glass"
                size="lg"
                :disabled="isSubmitting"
            >
                {{ isSubmitting ? 'Creating owner account...' : 'Create owner account' }}
            </Button>
        </form>
    </div>
</template>

<style scoped>
.bootstrap-light-aura {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: min(125vw, 920px);
    height: min(125vw, 920px);
    background: radial-gradient(
        circle at 50% 50%,
        rgba(45, 59, 78, 0.64) 0%,
        rgba(38, 50, 67, 0.3) 42%,
        rgba(38, 50, 67, 0.14) 70%,
        transparent 86%
    );
    filter: blur(46px);
    pointer-events: none;
    animation: auraFadeIn 1.2s ease-out forwards;
}

.bootstrap-light-source {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 320px;
    height: 320px;
    background: radial-gradient(
        circle at 50% 50%,
        rgba(62, 82, 109, 0.92) 0%,
        rgba(45, 59, 78, 0.56) 38%,
        transparent 74%
    );
    filter: blur(30px);
    pointer-events: none;
    animation: sourceFadeIn 0.9s ease-out forwards;
}

@keyframes auraFadeIn {
    0% {
        opacity: 0;
        transform: translate(-50%, -50%) scale(0.3);
    }
    100% {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1);
    }
}

@keyframes sourceFadeIn {
    0% {
        opacity: 0;
        transform: translate(-50%, -50%) scale(0);
    }
    100% {
        opacity: 1;
        transform: translate(-50%, -50%) scale(1);
    }
}
</style>
