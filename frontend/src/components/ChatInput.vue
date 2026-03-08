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
      placeholder="Type your message. Enter to send, Shift+Enter for newline."
      :disabled="disabled"
      rows="3"
      @keydown="onKeydown"
    />
    <div class="chat-actions">
      <button class="send-btn" :disabled="disabled || isStreaming || !draft.trim()" @click="onSend">
        Send
      </button>
      <button class="stop-btn" :disabled="!isStreaming" @click="$emit('stop')">Stop</button>
    </div>
  </footer>
</template>
