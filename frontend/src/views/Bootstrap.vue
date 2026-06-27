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
        <div class="pointer-events-none absolute left-1/2 top-1/2 z-0 h-[640px] w-[640px] -translate-x-1/2 -translate-y-[42%] rounded-full bg-[radial-gradient(circle,rgba(31,41,55,0.72)_0%,rgba(31,41,55,0.34)_42%,transparent_74%)]"></div>

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
