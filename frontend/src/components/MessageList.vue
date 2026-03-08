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
</script>

<template>
  <section ref="containerRef" class="message-list" @scroll="updateStickState">
    <div v-if="messages.length === 0" class="empty-state">
      <h2>Start a new conversation</h2>
      <p>Ask anything. The assistant will reply with streaming output.</p>
    </div>

    <template v-else>
      <div class="messages-container">
        <MessageBubble v-for="msg in messages" :key="msg.id" :message="msg" :show-thinking="showThinking" />
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

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.messages-end {
  height: 1px;
}
</style>
