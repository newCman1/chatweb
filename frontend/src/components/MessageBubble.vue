<script setup lang="ts">
import type { Message } from "@/types/chat";
import { computed } from "vue";

const props = defineProps<{
  message: Message;
  thinkingVisible: boolean;
}>();

defineEmits<{
  "toggle-thinking": [];
}>();

const isUser = computed(() => props.message.role === "user");
const hasThinking = computed(() => Boolean(props.message.thinking?.trim()));

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
</script>

<template>
  <article class="message-row" :class="message.role">
    <div class="message-avatar" :class="message.role">
      <span class="avatar-text">{{ isUser ? "You" : "AI" }}</span>
    </div>

    <div class="message-bubble-wrapper">
      <div class="message-bubble" :class="message.role">
        <div v-if="message.role === 'assistant' && hasThinking" class="thinking-wrap">
          <button class="thinking-chip" type="button" @click="$emit('toggle-thinking')">
            {{ thinkingVisible ? "Hide thinking" : "Show thinking" }}
          </button>
          <pre v-if="thinkingVisible" class="thinking-content">{{ message.thinking }}</pre>
        </div>

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
          <span class="status-dot"></span>
          {{ statusText }}
        </span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.message-row {
  display: flex;
  gap: 12px;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.message-avatar.user {
  background: var(--brand);
  color: #fff;
}

.message-avatar.assistant {
  background: #e2e8f0;
  color: var(--text-secondary);
}

.message-bubble-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 72%;
  gap: 6px;
}

.message-row.user .message-bubble-wrapper {
  align-items: flex-end;
}

.message-bubble {
  border-radius: 14px;
  padding: 12px 14px;
  border: 1px solid var(--border);
}

.message-bubble.user {
  background: var(--brand);
  color: #fff;
  border-color: var(--brand);
}

.message-bubble.assistant {
  background: #fff;
  color: var(--text-main);
}

.thinking-wrap {
  margin-bottom: 8px;
}

.thinking-chip {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-soft);
  cursor: pointer;
}

.thinking-chip:hover {
  border-color: var(--brand);
  color: var(--brand-strong);
}

.thinking-content {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-main);
  padding: 10px;
  background: var(--bg-soft);
  border-radius: 10px;
  line-height: 1.6;
}

.message-content {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  font-size: 14px;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 0 4px;
}

.message-row.user .message-meta {
  justify-content: flex-end;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text-tertiary);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--warning);
}

.status-indicator.streaming .status-dot {
  background: var(--brand);
}

.status-indicator.error .status-dot {
  background: var(--danger);
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 7px;
  height: 7px;
  background: var(--text-tertiary);
  border-radius: 50%;
  animation: typing-bounce 1.2s ease-in-out infinite both;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes typing-bounce {
  0%,
  80%,
  100% {
    opacity: 0.4;
    transform: translateY(0);
  }
  40% {
    opacity: 1;
    transform: translateY(-2px);
  }
}
</style>
