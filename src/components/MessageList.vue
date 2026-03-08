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
      <h2>开始你的第一个问题</h2>
      <p>这是桌面端聊天原型，已预留后端接口层。</p>
    </div>
    <MessageBubble v-for="msg in messages" :key="msg.id" :message="msg" />
  </section>
</template>
