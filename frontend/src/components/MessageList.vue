<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import type { Message } from "@/types/chat";
import MessageBubble from "./MessageBubble.vue";

const props = defineProps<{
  messages: Message[];
  showThinking: boolean;
}>();

const containerRef = ref<HTMLElement | null>(null);
const stickToBottom = ref(true);

function updateStickState() {
  const el = containerRef.value;
  if (!el) return;
  const distance = el.scrollHeight - el.scrollTop - el.clientHeight;
  stickToBottom.value = distance < 48;
}

async function scrollToBottom(force = false) {
  await nextTick();
  const el = containerRef.value;
  if (!el) return;
  if (stickToBottom.value || force) {
    el.scrollTop = el.scrollHeight;
  }
}

onMounted(() => {
  scrollToBottom(true);
});

watch(
  () => props.messages.map((msg) => `${msg.id}-${msg.content.length}-${msg.thinking?.length ?? 0}-${msg.status}`).join("|"),
  () => {
    scrollToBottom();
  }
);

const suggestions = [
  { icon: "💡", text: "Explain complex concepts" },
  { icon: "✍️", text: "Help me write an article" },
  { icon: "🐛", text: "Debug my code" },
  { icon: "🧠", text: "Brainstorm ideas" }
];
</script>

<template>
  <section ref="containerRef" class="message-list" @scroll="updateStickState">
    <div v-if="messages.length === 0" class="empty-state">
      <div class="empty-state-icon">🤖</div>
      <h2>Welcome to Chat AI</h2>
      <p>Your intelligent assistant. Ask anything and get helpful responses in real-time.</p>
      
      <div class="suggestions">
        <div 
          v-for="(suggestion, index) in suggestions" 
          :key="index"
          class="suggestion-item"
        >
          <span class="suggestion-icon">{{ suggestion.icon }}</span>
          <span class="suggestion-text">{{ suggestion.text }}</span>
        </div>
      </div>
    </div>

    <template v-else>
      <div class="messages-container">
        <MessageBubble 
          v-for="msg in messages" 
          :key="msg.id" 
          :message="msg" 
          :show-thinking="showThinking" 
        />
      </div>
      <div class="messages-end"></div>
    </template>
  </section>
</template>

<style scoped>
.message-list {
  overflow-y: auto;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: linear-gradient(180deg, var(--bg-panel) 0%, var(--bg-base) 100%);
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--text-tertiary);
  padding: 48px 24px;
  min-height: 400px;
}

.empty-state-icon {
  font-size: 72px;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
  filter: drop-shadow(0 10px 30px rgba(59, 130, 246, 0.3));
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-12px) rotate(3deg); }
}

.empty-state h2 {
  color: var(--text-main);
  font-size: 28px;
  font-weight: 800;
  margin: 0 0 12px;
  background: var(--brand-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.empty-state > p {
  margin: 0 0 32px;
  font-size: 15px;
  max-width: 420px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.suggestions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  max-width: 360px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
}

.suggestion-item:hover {
  border-color: var(--brand);
  background: var(--brand-soft);
  transform: translateX(8px);
  box-shadow: var(--shadow-md);
}

.suggestion-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.suggestion-text {
  font-weight: 500;
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.messages-end {
  height: 1px;
}
</style>
