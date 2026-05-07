<script setup>
import PageFooter from '../components/PageFooter.vue'
</script>

<template>
  <div class="landing-page">
    <div class="landing-center">
      <div class="landing-title" aria-label="Casefile Database">
        <span>CASE</span>
        <span>FILE</span>
        <span>dAtA</span>
        <span>bAse</span>
      </div>
    </div>
    <PageFooter class="landing-footer-override" />
  </div>
</template>

<style scoped>
.landing-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0 1.5rem;
}

.landing-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.landing-title {
  display: flex;
  flex-direction: column;
  font-family: 'Major Mono Display', monospace;
  font-size: clamp(2.8rem, 8vw, 7rem);
  line-height: 1.05;
  color: var(--text);
  text-align: center;
  user-select: none;
}
</style>
