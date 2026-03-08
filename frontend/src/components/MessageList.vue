<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import type { Message } from "@/types/chat";
import MessageBubble from "./MessageBubble.vue";

const props = defineProps<{
  messages: Message[];
  thinkingExpandedByMessageId: Record<string, boolean>;
}>();

defineEmits<{
  "toggle-thinking": [messageId: string];
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
  () =>
    props.messages.map((msg) => `${msg.id}-${msg.content.length}-${msg.thinking?.length ?? 0}-${msg.status}`).join("|"),
  () => {
    scrollToBottom();
  }
);

const suggestions = ["Explain a concept", "Write a draft", "Debug this code"];
</script>

<template>
  <section ref="containerRef" class="message-list" @scroll="updateStickState">
    <div v-if="messages.length === 0" class="empty-state">
      <h2>Start a new conversation</h2>
      <p>Type a message below. Responses stream in real time.</p>
      <div class="suggestions" aria-hidden="true">
        <span v-for="item in suggestions" :key="item" class="suggestion-item">{{ item }}</span>
      </div>
    </div>

    <template v-else>
      <div class="messages-container">
        <MessageBubble
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
          :thinking-visible="Boolean(thinkingExpandedByMessageId[msg.id])"
          @toggle-thinking="$emit('toggle-thinking', msg.id)"
        />
      </div>
      <div class="messages-end"></div>
    </template>
  </section>
</template>

<style scoped>
.message-list {
  overflow-y: auto;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--bg-base);
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--text-tertiary);
  padding: 32px 24px;
  min-height: 360px;
}

.empty-state h2 {
  color: var(--text-main);
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 10px;
}

.empty-state > p {
  margin: 0 0 20px;
  font-size: 15px;
  max-width: 380px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.suggestions {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 8px;
  width: 100%;
  max-width: 420px;
  justify-content: center;
}

.suggestion-item {
  display: inline-flex;
  align-items: center;
  padding: 7px 12px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 13px;
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
