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

        <Form
            variant="card"
        >
            <Heading
                class="mb-0"
                variant="h3"
            >
                Set up Mantask
            </Heading>

            <Text
                class="mb-5 text-center"
                color="secondary"
                size="sm"
            >
                Claim this Mantask instance and become owner.
            </Text>

            <Input
                id="username"
                size="md"
                type="text"
                placeholder="Username"
            />
            <Input
                id="email"
                size="md"
                type="email"
                placeholder="Email address"
            />
            <Input
                id="password"
                size="md"
                type="password"
                placeholder="Password"
            />
            <Input
                id="organization-name"
                size="md"
                type="text"
                placeholder="Organization name"
            />
            <Input
                id="team-name"
                size="md"
                type="text"
                placeholder="Team name"
            />
            <Input
                id="bootstrap-secret"
                size="md"
                type="password"
                placeholder="Bootstrap secret"
            />

            <Button
                variant="glass"
                size="lg"
            >
                Create owner account
            </Button>

            <Text
                class="mt-2"
                color="secondary"
                size="xs"
            >
                Already have an account?
                <Link
                    href="/login"
                    color="primary"
                    size="xs"
                >
                    Login
                </Link>
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
    width: min(110vw, 740px);
    height: min(110vw, 740px);
    background: radial-gradient(
        circle at 50% 50%,
        rgba(31, 41, 55, 0.50) 0%,
        rgba(31, 41, 55, 0.20) 45%,
        transparent 75%
    );
    filter: blur(55px);
    pointer-events: none;
}

.bootstrap-light-source {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 230px;
    height: 230px;
    background: radial-gradient(
        circle at 50% 50%,
        rgba(31, 41, 55, 0.85) 0%,
        rgba(31, 41, 55, 0.45) 35%,
        transparent 70%
    );
    filter: blur(34px);
    pointer-events: none;
}
</style>
