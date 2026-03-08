<script setup lang="ts">
import type { Message } from "@/types/chat";
import { computed } from "vue";

const props = defineProps<{
  message: Message;
}>();

const isUser = computed(() => props.message.role === "user");
const isAssistant = computed(() => props.message.role === "assistant");

const formattedTime = computed(() => {
  const date = new Date(props.message.createdAt);
  return date.toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
  });
});

const statusText = computed(() => {
  switch (props.message.status) {
    case "streaming":
      return "生成中...";
    case "error":
      return "生成失败";
    case "stopped":
      return "已停止";
    default:
      return "";
  }
});
</script>

<template>
  <article class="message-row" :class="message.role">
    <!-- 头像 -->
    <div class="message-avatar" :class="message.role">
      {{ isUser ? "我" : "AI" }}
    </div>

    <!-- 消息内容包装器 -->
    <div class="message-bubble-wrapper">
      <!-- 消息气泡 -->
      <div class="message-bubble" :class="message.role">
        <div class="message-content">{{ message.content }}</div>

        <!-- 打字指示器 -->
        <div v-if="message.status === 'streaming' && !message.content" class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <!-- 元信息 -->
      <div class="message-meta">
        <span class="message-time">{{ formattedTime }}</span>
        <span v-if="statusText" class="status-indicator" :class="message.status">
          {{ statusText }}
        </span>
      </div>
    </div>
  </article>
</template>
