<script setup lang="ts">
import type { Message } from "@/types/chat";
import { computed, ref, watch } from "vue";

const props = defineProps<{
  message: Message;
}>();

const isUser = computed(() => props.message.role === "user");
const hasThinking = computed(() => Boolean(props.message.thinking?.trim()));
const thinkingVisible = ref(false);

watch(
  () => props.message.id,
  () => {
    thinkingVisible.value = false;
  }
);

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

function toggleThinking() {
  thinkingVisible.value = !thinkingVisible.value;
}
</script>

<template>
  <article class="message-row" :class="message.role">
    <div class="message-avatar" :class="message.role">
      <span class="avatar-text">{{ isUser ? "You" : "AI" }}</span>
      <div v-if="!isUser" class="avatar-glow"></div>
    </div>

    <div class="message-bubble-wrapper">
      <div class="message-bubble" :class="message.role">
        <div v-if="message.role === 'assistant' && hasThinking" class="thinking-wrap">
          <button class="thinking-chip" type="button" @click="toggleThinking">
            {{ thinkingVisible ? "隐藏思考" : "显示思考" }}
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
  gap: 14px;
  animation: messageAppear 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes messageAppear {
  from {
    opacity: 0;
    transform: translateY(15px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
  position: relative;
}

.message-avatar:hover {
  transform: scale(1.1);
}

.message-avatar.user {
  background: var(--brand-gradient);
  color: white;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
}

.message-avatar.assistant {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  color: var(--text-secondary);
  border: 2px solid var(--border);
}

.avatar-text {
  position: relative;
  z-index: 1;
}

.avatar-glow {
  position: absolute;
  inset: -2px;
  background: var(--brand-gradient);
  border-radius: 50%;
  opacity: 0;
  filter: blur(8px);
  transition: opacity var(--transition-fast);
  z-index: 0;
}

.message-avatar.assistant:hover .avatar-glow {
  opacity: 0.3;
}

.message-bubble-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 70%;
  gap: 6px;
}

.message-row.user .message-bubble-wrapper {
  align-items: flex-end;
}

.message-bubble {
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  position: relative;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}

.message-bubble:hover {
  box-shadow: var(--shadow-md);
}

.message-bubble.user {
  background: var(--brand-gradient);
  color: white;
  border-bottom-right-radius: var(--radius-sm);
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
}

.message-bubble.assistant {
  background: var(--bg-panel);
  color: var(--text-main);
  border: 1px solid var(--border);
  border-bottom-left-radius: var(--radius-sm);
}

.thinking-wrap {
  margin-bottom: 10px;
}

.thinking-chip {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 10px;
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
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-word;
  font-family: var(--font-main);
  padding: 12px;
  background: var(--bg-soft);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--brand);
  line-height: 1.6;
}

.message-content {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
  font-size: 15px;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 0 4px;
}

.message-row.user .message-meta {
  justify-content: flex-end;
}

.message-time {
  font-weight: 500;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--text-tertiary);
  padding: 4px 10px;
  background: var(--bg-soft);
  border-radius: 999px;
  font-weight: 600;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--warning);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.4;
    transform: scale(0.8);
  }
}

.status-indicator.streaming .status-dot {
  background: var(--brand);
}

.status-indicator.error .status-dot {
  background: var(--danger);
  animation: none;
}

.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--text-tertiary);
  border-radius: 50%;
  animation: typingBounce 1.4s ease-in-out infinite both;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typingBounce {
  0%,
  80%,
  100% {
    transform: scale(0.6);
    opacity: 0.4;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
