<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useData, allItems } from '../composables/useData.js'
import {
  completed, mnesia, addKey, removeKey, setMnesia,
  mediaKey, authorKey, showKey,
} from '../composables/useCompletion.js'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['close'])

const { data, ensureLoaded } = useData()
const search = ref('')
const pendingConfirm = ref(null) // option awaiting an author/show confirmation

watch(() => props.open, (v) => {
  if (v) ensureLoaded()
  else { search.value = ''; pendingConfirm.value = null }
})

function onKey(e) {
  if (e.key === 'Escape' && props.open) close()
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))

const showCounts = computed(() => {
  const map = new Map()
  for (const s of (data.value.tv_shows || [])) {
    map.set(s.title, (s.episodes || []).length)
  }
  for (const ep of (data.value.tv_episodes || [])) {
    const k = ep.series_name || ep.title
    map.set(k, (map.get(k) || 0) + 1)
  }
  return map
})

const authorCounts = computed(() => {
  const map = new Map()
  for (const m of allItems.value) {
    if (!m.creator) continue
    map.set(m.creator, (map.get(m.creator) || 0) + 1)
  }
  return map
})

const options = computed(() => {
  const out = []
  for (const [name, n] of showCounts.value) {
    out.push({
      type: 'show',
      key: showKey(name),
      label: name,
      sub: `show · ${n} episode${n === 1 ? '' : 's'}`,
      count: n,
    })
  }
  for (const [name, n] of authorCounts.value) {
    out.push({
      type: 'author',
      key: authorKey(name),
      label: name,
      sub: `author · ${n} work${n === 1 ? '' : 's'}`,
      count: n,
    })
  }
  for (const m of allItems.value) {
    const sub = [m.media_type, m.year, m.creator].filter(Boolean).join(' · ')
    out.push({
      type: 'media',
      key: mediaKey(m.slug),
      label: m.title,
      sub,
    })
  }
  return out
})

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return []
  return options.value
    .filter(o => !completed.value.has(o.key))
    .filter(o => o.label.toLowerCase().includes(q) || o.sub.toLowerCase().includes(q))
    .slice(0, 20)
})

const completedItems = computed(() => {
  const byKey = new Map(options.value.map(o => [o.key, o]))
  return [...completed.value].map(k => byKey.get(k) || { type: 'unknown', key: k, label: k, sub: '' })
})

function selectOption(opt) {
  if (opt.type === 'author' || opt.type === 'show') {
    pendingConfirm.value = opt
    return
  }
  addKey(opt.key)
  search.value = ''
}

function confirmPending() {
  if (!pendingConfirm.value) return
  addKey(pendingConfirm.value.key)
  pendingConfirm.value = null
  search.value = ''
}

function cancelPending() {
  pendingConfirm.value = null
}

function close() {
  emit('close')
}
</script>

<template>
  <div v-if="open" class="modal-overlay" @click.self="close">
    <div class="modal-card" role="dialog" aria-modal="true" aria-label="Mark as completed">
      <div class="modal-header">
        <h2 class="modal-title">Mark as completed</h2>
        <button type="button" class="close-btn" @click="close" aria-label="Close">×</button>
      </div>

      <p class="muted modal-blurb">
        Spoilers stay hidden until you mark a work, show, or author as completed.
        Your list lives in this browser only.
      </p>

      <label class="mnesia-row">
        <input
          type="checkbox"
          :checked="mnesia"
          @change="setMnesia($event.target.checked)"
        />
        <span>
          <strong>Mnesia mode</strong>
          <span class="muted"> — reveal everything everywhere, ignoring the completed list.</span>
        </span>
      </label>

      <div v-if="pendingConfirm" class="confirm-box">
        <p style="margin:0 0 0.6rem">
          <strong>{{ pendingConfirm.label }}</strong> is
          <template v-if="pendingConfirm.type === 'author'">an author with {{ pendingConfirm.count }} work{{ pendingConfirm.count === 1 ? '' : 's' }} on file</template>
          <template v-else>a show with {{ pendingConfirm.count }} episode{{ pendingConfirm.count === 1 ? '' : 's' }} on file</template>.
          Marking it as completed will reveal spoilers for
          <strong>
            <template v-if="pendingConfirm.type === 'author'">every work by this author</template>
            <template v-else>every episode of this show</template>
          </strong>.
          Continue?
        </p>
        <div class="confirm-actions">
          <button type="button" class="btn-primary" @click="confirmPending">Yes, mark as completed</button>
          <button type="button" @click="cancelPending">Cancel</button>
        </div>
      </div>

      <template v-else>
        <input
          v-model="search"
          type="text"
          placeholder="Type a title, show name, or author…"
          autocomplete="off"
          class="modal-search"
        />

        <ul v-if="filtered.length" class="autocomplete-list">
          <li v-for="o in filtered" :key="o.key" @click="selectOption(o)" class="autocomplete-item">
            <span class="ac-label">{{ o.label }}</span>
            <span class="ac-sub muted">{{ o.sub }}</span>
            <span class="ac-type-pill" :data-type="o.type">{{ o.type }}</span>
          </li>
        </ul>
        <p v-else-if="search" class="muted modal-empty">No matches.</p>
      </template>

      <h3 class="modal-section-h">Currently marked ({{ completedItems.length }})</h3>
      <p v-if="!completedItems.length" class="muted modal-empty">Nothing marked yet.</p>
      <ul v-else class="completed-list">
        <li v-for="o in completedItems" :key="o.key" class="completed-item">
          <span class="ac-label">{{ o.label }}</span>
          <span class="ac-sub muted">{{ o.sub }}</span>
          <button type="button" class="unmark-btn" @click="removeKey(o.key)" aria-label="Unmark">×</button>
        </li>
      </ul>
    </div>
  </div>
</template>
