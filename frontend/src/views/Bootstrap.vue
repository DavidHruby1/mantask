<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
import Container from '@/components/ui/Container.vue'
import Link from '@/components/ui/Link.vue'
import Input from '@/components/ui/Input.vue'
import Text from '@/components/ui/Text.vue'
import Heading from '@/components/ui/Heading.vue'
import Form from '@/components/ui/Form.vue'
</script>

<template>
    <Container>
        <div class="bootstrap-light-aura"></div>
        <div class="bootstrap-light-source"></div>

        <Form variant="card">
            <Heading class="mb-0" variant="h3"> Set up Mantask </Heading>

            <Text class="mb-5 text-center" color="secondary" size="sm">
                Claim this Mantask instance and become owner.
            </Text>

            <Input
                id="username"
                aria-label="Username"
                size="md"
                type="text"
                placeholder="Username"
            />
            <Input
                id="email"
                aria-label="Email address"
                size="md"
                type="email"
                placeholder="Email address"
            />
            <Input
                id="password"
                aria-label="Password"
                size="md"
                type="password"
                placeholder="Password"
            />
            <Input
                id="organization-name"
                aria-label="Organization name"
                size="md"
                type="text"
                placeholder="Organization name"
            />
            <Input
                id="team-name"
                aria-label="Team name"
                size="md"
                type="text"
                placeholder="Team name"
            />
            <Input
                id="bootstrap-secret"
                aria-label="Bootstrap secret"
                size="md"
                type="password"
                placeholder="Bootstrap secret"
            />

            <Button variant="glass" size="lg"> Create owner account </Button>

            <Text class="mt-2" color="secondary" size="xs">
                Already have an account?
                <Link href="/login" color="primary" size="xs"> Login </Link>
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
    width: min(115vw, 800px);
    height: min(115vw, 800px);
    background: radial-gradient(
        circle at 50% 50%,
        rgba(31, 41, 55, 0.62) 0%,
        rgba(31, 41, 55, 0.28) 45%,
        transparent 75%
    );
    filter: blur(55px);
    pointer-events: none;
    animation: auraFadeIn 1.2s ease-out forwards;
}

.bootstrap-light-source {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 240px;
    height: 240px;
    background: radial-gradient(
        circle at 50% 50%,
        rgba(31, 41, 55, 0.95) 0%,
        rgba(31, 41, 55, 0.55) 35%,
        transparent 70%
    );
    filter: blur(34px);
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
