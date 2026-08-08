<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
import Container from '@/components/ui/Container.vue'
import Link from '@/components/ui/Link.vue'
import Input from '@/components/ui/Input.vue'
import Text from '@/components/ui/Text.vue'
import Heading from '@/components/ui/Heading.vue'
import Form from '@/components/ui/Form.vue'
import {
    validateBootstrapSecret,
    validateEmail,
    validateOrganizationOrTeamName,
    validatePassword,
    validateUsername,
} from '@/utils/validation'

import { ref } from 'vue'

const username = ref<string>('')
const email = ref<string>('')
const password = ref<string>('')
const organization = ref<string>('')
const team = ref<string>('')
const bootstrapSecret = ref<string>('')
const formErrors = ref<Record<string, string>>({
    username: '',
    email: '',
    password: '',
    organization: '',
    team: '',
    bootstrapSecret: '',
})

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

// This function will use store to send data to backend
// Then it will recieve result of the operation and act accordingly
// 1. it validates the whole form
function handleBootstrapSubmit() {
    if (!validateBootstrapForm()) return

}
</script>

<template>
    <Container>
        <div class="bootstrap-light-aura"></div>
        <div class="bootstrap-light-source"></div>

        <Form
            variant="card"
            @submit-form="handleBootstrapSubmit"
        >
            <Heading class="mb-0" variant="h3"> Set up Mantask </Heading>

            <Text class="mb-5 text-center" color="secondary" size="sm">
                Claim this Mantask instance and become owner.
            </Text>

            <Input
                v-model="username"
                id="username"
                aria-label="Username"
                size="md"
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
                size="md"
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
                size="md"
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
                size="md"
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
                size="md"
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
                size="md"
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
            >
                Create owner account
            </Button>

            <Text class="mt-2" color="secondary" size="xs">
                Already have an account?
                <Link :to="{ name: 'login' }" color="primary" size="xs"> Login </Link>
            </Text>
        </Form>
    </Container>
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
