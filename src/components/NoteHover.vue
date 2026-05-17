<script setup>
const props = defineProps({ text: String })
</script>

<template>
  <span v-if="!text" class="muted">-</span>
  <span v-else>{{ text }}</span>
</template>
