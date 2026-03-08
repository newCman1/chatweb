<script setup lang="ts">
import type { Message } from "@/types/chat";
import { computed } from "vue";

const props = defineProps<{
  message: Message;
  showThinking: boolean;
}>();

const isUser = computed(() => props.message.role === "user");

const formattedTime = computed(() => {
  const date = new Date(props.message.createdAt);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit"
  });
});

const statusText = computed(() => {
  switch (props.message.status) {
    case "streaming":
      return "Generating...";
    case "error":
      return "Failed";
    case "stopped":
      return "Stopped";
    default:
      return "";
  }
});

const hasThinking = computed(() => Boolean(props.message.thinking?.trim()));
</script>

<template>
  <article class="message-row" :class="message.role">
    <div class="message-avatar" :class="message.role">
      {{ isUser ? "You" : "AI" }}
    </div>

    <div class="message-bubble-wrapper">
      <div class="message-bubble" :class="message.role">
        <details v-if="message.role === 'assistant' && showThinking && hasThinking" class="thinking-box">
          <summary>Thinking</summary>
          <pre class="thinking-content">{{ message.thinking }}</pre>
        </details>

        <div class="message-content">{{ message.content }}</div>

        <div v-if="message.status === 'streaming' && !message.content" class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <div class="message-meta">
        <span class="message-time">{{ formattedTime }}</span>
        <span v-if="statusText" class="status-indicator" :class="message.status">
          {{ statusText }}
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.thinking-box {
  margin-bottom: 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-panel);
  padding: 6px 8px;
}

.thinking-box summary {
  cursor: pointer;
  font-size: 12px;
  color: var(--text-secondary);
  user-select: none;
}

.thinking-content {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-main);
}
</style>
