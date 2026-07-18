<template>
  <div class="chat-layout">
    <div class="header">
      <h1>Ask the Baker</h1>
      <button v-if="messages.length" class="btn-sm btn-ghost" @click="clear">Clear</button>
    </div>

    <div class="messages" ref="messagesEl">
      <p v-if="!messages.length" class="placeholder">
        Ask anything about sourdough — troubleshooting, hydration, schedules, techniques.
      </p>
      <div v-for="(msg, i) in messages" :key="i" :class="['msg', msg.role]">
        <div class="bubble">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="msg assistant">
        <div class="bubble thinking">Thinking...</div>
      </div>
    </div>

    <div class="input-row">
      <textarea
        v-model="input"
        rows="2"
        placeholder="Ask the sourdough expert..."
        @keydown.enter.exact.prevent="send"
      />
      <button class="btn-primary" :disabled="!input.trim() || loading" @click="send">Send</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { apiFetch } from '@/api'
import type { ChatMessage } from '@/types'

const messages = ref<ChatMessage[]>([])
const input = ref('')
const loading = ref(false)
const messagesEl = ref<HTMLElement>()

async function send() {
  const content = input.value.trim()
  if (!content || loading.value) return
  input.value = ''
  messages.value = [...messages.value, { role: 'user', content }]
  loading.value = true
  await scrollBottom()
  try {
    const res = await apiFetch<{ reply: string }>('/ollama/chat', {
      method: 'POST',
      body: JSON.stringify({ messages: messages.value }),
    })
    messages.value = [...messages.value, { role: 'assistant', content: res.reply }]
  } catch (e) {
    messages.value = [...messages.value, { role: 'assistant', content: `Error: ${(e as Error).message}` }]
  } finally {
    loading.value = false
    await scrollBottom()
  }
}

function clear() {
  messages.value = []
}

async function scrollBottom() {
  await nextTick()
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
}
</script>

<style scoped>
.chat-layout { display: flex; flex-direction: column; height: calc(100vh - 120px); }
.header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem; }
h1 { font-size: 1.4rem; }
.btn-ghost { background: none; border: 1px solid var(--border, #ccc); color: var(--text-muted); border-radius: 4px; padding: 0.2rem 0.6rem; cursor: pointer; font-size: 0.8rem; }
.messages { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem 0; }
.placeholder { color: var(--text-muted); font-style: italic; text-align: center; margin-top: 2rem; }
.msg { display: flex; }
.msg.user { justify-content: flex-end; }
.msg.assistant { justify-content: flex-start; }
.bubble { max-width: 75%; padding: 0.6rem 0.9rem; border-radius: 12px; font-size: 0.9rem; white-space: pre-wrap; line-height: 1.5; }
.msg.user .bubble { background: var(--accent); color: #fff; border-bottom-right-radius: 3px; }
.msg.assistant .bubble { background: var(--surface); border: 1px solid var(--border); border-bottom-left-radius: 3px; }
.thinking { color: var(--text-muted); font-style: italic; }
.input-row { display: flex; gap: 0.5rem; margin-top: 0.75rem; }
.input-row textarea { flex: 1; resize: none; }
.input-row button { align-self: flex-end; }
</style>
