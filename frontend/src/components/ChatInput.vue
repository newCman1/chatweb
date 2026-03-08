<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
  disabled?: boolean;
  isStreaming: boolean;
}>();

const emit = defineEmits<{
  send: [content: string];
  stop: [];
}>();

const draft = ref("");

function onSend() {
  const content = draft.value.trim();
  if (!content || props.disabled || props.isStreaming) return;
  emit("send", content);
  draft.value = "";
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    onSend();
  }
}
</script>

<template>
  <footer class="chat-input-wrap">
    <textarea
      v-model="draft"
      class="chat-input"
      placeholder="输入消息，Enter 发送，Shift+Enter 换行"
      :disabled="disabled"
      rows="3"
      @keydown="onKeydown"
    />
    <div class="chat-actions">
      <button class="send-btn" :disabled="disabled || isStreaming || !draft.trim()" @click="onSend">
        发送
      </button>
      <button class="stop-btn" :disabled="!isStreaming" @click="$emit('stop')">停止生成</button>
    </div>
  </footer>
</template>
