<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
</script>

<template>
  <div class="flex min-h-screen items-center justify-center">
    <div class="flex flex-col items-center gap-4">
      <Button variant="primary" size="lg">Get Started</Button>
      <Button variant="secondary" size="md">Learn More</Button>
      <Button variant="ghost" size="sm">Cancel</Button>
      <Button variant="primary" size="md" disabled>Disabled</Button>
    </div>
  </div>
</template>
