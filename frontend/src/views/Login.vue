<script setup lang="ts">
import Button from '@/components/ui/Button.vue'
</script>

<template>
  <div class="login-page">
    <div class="light-aura"></div>
    <div class="light-beam"></div>
    <div class="light-source"></div>

    <div class="flex flex-col items-center gap-4 relative z-10">
      <Button variant="primary" size="lg">Get Started</Button>
      <Button variant="secondary" size="md">Learn More</Button>
      <Button variant="ghost" size="sm">Cancel</Button>
      <Button variant="primary" size="md" disabled>Disabled</Button>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.light-aura {
  position: absolute;
  top: -60px;
  left: 50%;
  transform: translateX(-50%);
  width: 140vw;
  height: 60vh;
  background: radial-gradient(
    ellipse 48% 80% at 50% 0%,
    rgba(31, 41, 55, 0.38) 0%,
    rgba(31, 41, 55, 0.12) 55%,
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
    rgba(31, 41, 55, 0.85) 0%,
    rgba(31, 41, 55, 0.45) 30%,
    rgba(31, 41, 55, 0.15) 65%,
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
    rgba(31, 41, 55, 0.6) 0%,
    rgba(31, 41, 55, 0.15) 60%,
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
    rgba(31, 41, 55, 0.2) 0%,
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
  background: radial-gradient(
    circle,
    rgba(31, 41, 55, 0.7) 0%,
    transparent 70%
  );
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
