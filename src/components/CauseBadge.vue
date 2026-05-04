<script setup>
const props = defineProps({ cause: String, subtype: String })

function label(c) {
  if (!c) return 'Unknown'
  return c.charAt(0) + c.slice(1).toLowerCase().replace(/_/g, ' ')
}
</script>

<template>
  <span :class="['badge', `cause-${cause}`]">
    {{ label(cause) }}<span v-if="subtype" class="muted" style="margin-left:0.25rem;font-weight:400"> ({{ subtype }})</span>
  </span>
</template>
