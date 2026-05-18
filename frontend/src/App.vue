<script setup>
import { nextTick, ref } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const quickPrompts = [
  '北京今天天气怎么样？',
  '上海现在冷不冷？',
  '深圳适合出门吗？',
  '杭州会下雨吗？',
]

const welcomeText =
  '你好，我是天气查询智能体。你可以直接问我城市天气，我会以气泡形式流式回复。'

const input = ref('')
const isStreaming = ref(false)
const statusText = ref('就绪')
const errorText = ref('')
const chatListRef = ref(null)
const messages = ref(createWelcomeMessages())

function createId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }

  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function formatTime(date = new Date()) {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function createMessage(role, content, streaming = false) {
  return {
    id: createId(),
    role,
    content,
    streaming,
    time: formatTime(),
  }
}

function createWelcomeMessages() {
  return [createMessage('assistant', welcomeText)]
}

function ensureResponseOk(response) {
  if (!response.ok) {
    return response.text().then((body) => {
      throw new Error(body || `请求失败（${response.status}）`)
    })
  }

  return Promise.resolve()
}

function scrollToBottom() {
  nextTick(() => {
    const container = chatListRef.value

    if (!container) {
      return
    }

    container.scrollTop = container.scrollHeight
  })
}

function clearChat() {
  if (isStreaming.value) {
    return
  }

  messages.value = createWelcomeMessages()
  errorText.value = ''
  statusText.value = '就绪'
  scrollToBottom()
}

function handleKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

async function sendQuickPrompt(prompt) {
  if (isStreaming.value) {
    return
  }

  input.value = prompt
  await sendMessage()
}

async function sendMessage() {
  const question = input.value.trim()

  if (!question || isStreaming.value) {
    return
  }

  const userMessage = createMessage('user', question)
  const assistantMessage = createMessage('assistant', '正在思考并查询天气…', true)

  messages.value.push(userMessage, assistantMessage)
  input.value = ''
  errorText.value = ''
  isStreaming.value = true
  statusText.value = '正在查询天气…'
  scrollToBottom()

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: question }),
    })

    await ensureResponseOk(response)

    if (!response.body) {
      const fallbackText = await response.text()
      assistantMessage.content = fallbackText || '没有收到回复。'
      return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let streamedText = ''

    while (true) {
      const { value, done } = await reader.read()

      if (done) {
        break
      }

      streamedText += decoder.decode(value, { stream: true })
      assistantMessage.content = streamedText || '正在思考并查询天气…'
      scrollToBottom()
    }

    streamedText += decoder.decode()
    assistantMessage.content = streamedText.trim() || assistantMessage.content

    if (assistantMessage.content.startsWith('[ERROR]')) {
      assistantMessage.role = 'error'
      assistantMessage.content = assistantMessage.content.replace(/^\[ERROR]\s*/, '⚠️ ')
      errorText.value = assistantMessage.content
      statusText.value = '连接异常'
    } else {
      assistantMessage.role = 'assistant'
      statusText.value = '就绪'
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : '请求失败，请检查后端是否启动'
    assistantMessage.role = 'error'
    assistantMessage.content = `⚠️ ${message}`
    errorText.value = message
    statusText.value = '连接异常'
  } finally {
    assistantMessage.streaming = false
    isStreaming.value = false
    scrollToBottom()
  }
}
</script>

<template>
  <main class="page-shell">
    <section class="chat-card">
      <header class="hero">
        <div>
          <p class="eyebrow">Weather Agent</p>
          <h1>天气查询智能体</h1>
          <p class="subtitle">
            输入城市名或天气问题，智能体会以气泡形式流式回复，并保留历史对话。
          </p>
        </div>

        <div class="status-pill" :class="isStreaming ? 'status-pill--busy' : 'status-pill--ready'">
          <span class="status-dot"></span>
          <span>{{ isStreaming ? '思考中 / 流式输出中' : statusText }}</span>
        </div>
      </header>

      <div class="quick-actions" aria-label="快捷提问">
        <button
          v-for="prompt in quickPrompts"
          :key="prompt"
          type="button"
          class="quick-chip"
          :disabled="isStreaming"
          @click="sendQuickPrompt(prompt)"
        >
          {{ prompt }}
        </button>
      </div>

      <div ref="chatListRef" class="chat-window" role="log" aria-live="polite">
        <article
          v-for="message in messages"
          :key="message.id"
          class="bubble-row"
          :class="`bubble-row--${message.role}`"
        >
          <div class="bubble-meta">
            <span class="avatar">{{ message.role === 'user' ? '你' : 'AI' }}</span>
            <span class="time">{{ message.time }}</span>
          </div>

          <div class="bubble" :class="`bubble--${message.role}`">
            <p class="bubble-text">{{ message.content }}</p>
            <span v-if="message.streaming" class="typing-cursor" aria-hidden="true"></span>
          </div>
        </article>
      </div>

      <div class="composer">
        <label class="sr-only" for="prompt">请输入天气问题</label>
        <textarea
          id="prompt"
          v-model="input"
          class="composer-input"
          rows="1"
          placeholder="例如：北京今天天气怎么样？"
          :disabled="isStreaming"
          @keydown="handleKeydown"
        />

        <div class="composer-actions">
          <button type="button" class="ghost-button" :disabled="isStreaming" @click="clearChat">
            清空
          </button>
          <button
            type="button"
            class="send-button"
            :disabled="isStreaming || !input.trim()"
            @click="sendMessage"
          >
            {{ isStreaming ? '发送中…' : '发送' }}
          </button>
        </div>
      </div>

      <p v-if="errorText" class="error-banner">{{ errorText }}</p>
    </section>
  </main>
</template>

<style scoped>
:global(html),
:global(body),
:global(#app) {
  width: 100%;
  height: 100%;
  margin: 0;
}

:global(body) {
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background:
    radial-gradient(circle at top, rgba(96, 165, 250, 0.35), transparent 28%),
    linear-gradient(180deg, #eff6ff 0%, #e0f2fe 48%, #f8fafc 100%);
  color: #0f172a;
}

.page-shell {
  min-height: 100%;
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: stretch;
  box-sizing: border-box;
}

.chat-card {
  width: min(1120px, 100%);
  min-height: calc(100vh - 48px);
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 24px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px);
  box-shadow: 0 24px 70px rgba(15, 23, 42, 0.12);
}

.hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 0.8rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #2563eb;
  font-weight: 700;
}

.hero h1 {
  margin: 0;
  font-size: clamp(1.8rem, 3vw, 2.6rem);
  line-height: 1.1;
}

.subtitle {
  margin: 10px 0 0;
  color: #475569;
  line-height: 1.7;
  max-width: 60ch;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  font-size: 0.92rem;
  white-space: nowrap;
}

.status-pill--ready {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.status-pill--busy {
  background: rgba(37, 99, 235, 0.12);
  color: #1d4ed8;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: currentColor;
  box-shadow: 0 0 0 4px color-mix(in srgb, currentColor 18%, transparent);
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-chip {
  border: 1px solid rgba(37, 99, 235, 0.16);
  background: rgba(255, 255, 255, 0.9);
  color: #1d4ed8;
  border-radius: 999px;
  padding: 10px 14px;
  cursor: pointer;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    border-color 0.18s ease;
}

.quick-chip:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: rgba(37, 99, 235, 0.35);
  box-shadow: 0 10px 26px rgba(37, 99, 235, 0.12);
}

.quick-chip:disabled,
.ghost-button:disabled,
.send-button:disabled,
.composer-input:disabled {
  cursor: not-allowed;
  opacity: 0.65;
}

.chat-window {
  flex: 1;
  min-height: 420px;
  padding: 8px 4px 8px 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.bubble-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bubble-row--user {
  align-items: flex-end;
}

.bubble-row--assistant,
.bubble-row--error {
  align-items: flex-start;
}

.bubble-meta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 0.82rem;
}

.avatar {
  display: inline-grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #0f172a;
  font-weight: 700;
}

.bubble-row--user .avatar {
  background: #2563eb;
  color: white;
}

.bubble {
  max-width: min(72ch, 86%);
  padding: 14px 16px;
  border-radius: 22px;
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
}

.bubble--user {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  border-bottom-right-radius: 8px;
}

.bubble--assistant {
  background: rgba(255, 255, 255, 0.95);
  color: #0f172a;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-bottom-left-radius: 8px;
}

.bubble--error {
  background: rgba(254, 242, 242, 0.98);
  color: #b91c1c;
  border: 1px solid rgba(248, 113, 113, 0.28);
  border-bottom-left-radius: 8px;
}

.bubble-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.75;
}

.typing-cursor {
  display: inline-block;
  width: 8px;
  height: 18px;
  margin-left: 4px;
  vertical-align: text-bottom;
  background: currentColor;
  border-radius: 999px;
  animation: blink 1s steps(1, end) infinite;
}

.composer {
  position: sticky;
  bottom: 0;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 14px;
  align-items: end;
  padding: 16px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.18);
  box-shadow: 0 16px 30px rgba(15, 23, 42, 0.08);
}

.composer-input {
  width: 100%;
  min-height: 54px;
  max-height: 180px;
  resize: vertical;
  border: 1px solid rgba(148, 163, 184, 0.32);
  border-radius: 18px;
  padding: 14px 16px;
  font: inherit;
  line-height: 1.7;
  color: #0f172a;
  background: white;
  outline: none;
  box-sizing: border-box;
}

.composer-input:focus {
  border-color: rgba(37, 99, 235, 0.55);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}

.composer-actions {
  display: flex;
  gap: 10px;
}

.ghost-button,
.send-button {
  border: none;
  border-radius: 16px;
  padding: 14px 18px;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    opacity 0.18s ease;
}

.ghost-button:hover:not(:disabled),
.send-button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.ghost-button {
  background: #e2e8f0;
  color: #0f172a;
}

.send-button {
  color: white;
  background: linear-gradient(135deg, #0f172a, #2563eb);
  box-shadow: 0 14px 26px rgba(37, 99, 235, 0.22);
}

.error-banner {
  margin: 0;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(254, 242, 242, 0.96);
  color: #b91c1c;
  border: 1px solid rgba(248, 113, 113, 0.25);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@keyframes blink {
  0%,
  50% {
    opacity: 1;
  }

  51%,
  100% {
    opacity: 0;
  }
}

@media (max-width: 768px) {
  .page-shell {
    padding: 12px;
  }

  .chat-card {
    min-height: calc(100vh - 24px);
    padding: 16px;
    border-radius: 22px;
  }

  .hero {
    flex-direction: column;
  }

  .bubble {
    max-width: 100%;
  }

  .composer {
    grid-template-columns: 1fr;
  }

  .composer-actions {
    justify-content: flex-end;
  }
}
</style>
