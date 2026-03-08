<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import type { Message } from "@/types/chat";
import MessageBubble from "./MessageBubble.vue";

const props = defineProps<{
  messages: Message[];
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
  () => props.messages.map((msg) => `${msg.id}-${msg.content.length}-${msg.status}`).join("|"),
  () => {
    scrollToBottom();
  }
);
</script>

<template>
  <section ref="containerRef" class="message-list" @scroll="updateStickState">
    <div v-if="messages.length === 0" class="empty-state">
      <div class="empty-state-icon">🤖</div>
      <h2>开始你的对话</h2>
      <p>我是你的 AI 助手，可以回答问题、协助创作、讨论想法</p>
      <div class="suggestions">
        <div class="suggestion-item">
          <span class="suggestion-icon">💡</span>
          <span>解释复杂概念</span>
        </div>
        <div class="suggestion-item">
          <span class="suggestion-icon">✍️</span>
          <span>协助写作创作</span>
        </div>
        <div class="suggestion-item">
          <span class="suggestion-icon">💻</span>
          <span>编程问题解答</span>
        </div>
      </div>
    </div>
    
    <template v-else>
      <div class="messages-container">
        <MessageBubble v-for="msg in messages" :key="msg.id" :message="msg" />
      </div>
      <div class="messages-end"></div>
    </template>
  </section>
</template>

<style scoped>
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
  font-size: 64px;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.empty-state h2 {
  color: var(--text-main);
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 12px;
}

.empty-state > p {
  margin: 0 0 32px;
  font-size: 15px;
  max-width: 400px;
  line-height: 1.6;
}

.suggestions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 320px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.suggestion-item:hover {
  background: var(--bg-panel);
  border-color: var(--brand);
  transform: translateX(4px);
}

.suggestion-icon {
  font-size: 20px;
}

.suggestion-item span:last-child {
  font-size: 14px;
  color: var(--text-secondary);
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.messages-end {
  height: 1px;
}
</style>
