<script setup>
const props = defineProps({ text: String })
</script>

<template>
  <span v-if="!text" class="muted">-</span>
  <span v-else class="note-hover">
    <span class="note-trigger">Hover to expand</span>
    <span class="note-popover sensitive">{{ text }}</span>
  </span>
</template>
