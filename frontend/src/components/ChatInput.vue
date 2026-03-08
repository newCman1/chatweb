<script setup lang="ts">
import { ref } from "vue";

const props = defineProps<{
  disabled?: boolean;
  isStreaming: boolean;
  enableDeepThinking: boolean;
}>();

const emit = defineEmits<{
  send: [content: string];
  stop: [];
  "update:enableDeepThinking": [value: boolean];
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

function onToggleDeepThinking(event: Event) {
  const target = event.target as HTMLInputElement;
  emit("update:enableDeepThinking", target.checked);
}
</script>

<template>
  <footer class="chat-input-wrap">
    <div class="chat-input-container">
      <textarea
        v-model="draft"
        class="chat-input"
        placeholder="Type your message..."
        :disabled="disabled"
        rows="3"
        @keydown="onKeydown"
      />
      <div class="chat-input-toolbar">
        <span class="input-hint">
          <kbd>Enter</kbd> to send · <kbd>Shift</kbd> + <kbd>Enter</kbd> for new line
        </span>
      </div>
    </div>

    <div class="compose-options">
      <label class="thinking-toggle">
        <input type="checkbox" :checked="enableDeepThinking" @change="onToggleDeepThinking" />
        <span class="toggle-text">启用深度思考</span>
      </label>
    </div>

    <div class="chat-actions">
      <button class="stop-btn" :disabled="!isStreaming" @click="$emit('stop')">Stop</button>
      <button class="send-btn" :disabled="disabled || isStreaming || !draft.trim()" @click="onSend">
        Send
      </button>
    </div>
  </footer>
</template>

<style scoped>
.chat-input-wrap {
  border-top: 1px solid var(--border);
  padding: 20px 24px 24px;
  background: var(--bg-panel);
}

.chat-input-container {
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 6px;
  transition: all var(--transition-fast);
}

.chat-input-container:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 4px var(--brand-soft);
}

.chat-input {
  width: 100%;
  min-height: 56px;
  max-height: 200px;
  padding: 14px 18px;
  border: none;
  border-radius: var(--radius-lg);
  background: transparent;
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-main);
  resize: none;
  outline: none;
  font-family: var(--font-main);
}

.chat-input::placeholder {
  color: var(--text-tertiary);
}

.chat-input-toolbar {
  padding: 10px 14px;
  border-top: 1px solid var(--border-light);
  margin-top: 6px;
}

.input-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.input-hint kbd {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2px 6px;
  font-family: var(--font-mono);
  font-size: 11px;
}

.compose-options {
  margin-top: 10px;
}

.thinking-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-soft);
  font-size: 13px;
  color: var(--text-secondary);
  user-select: none;
}

.thinking-toggle input {
  margin: 0;
}

.chat-actions {
  margin-top: 10px;
  display: inline-flex;
  gap: 8px;
}

.chat-actions button {
  border: none;
  border-radius: var(--radius-md);
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.send-btn {
  background: var(--brand-gradient);
  color: #fff;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stop-btn {
  background: var(--danger-soft);
  color: var(--danger);
}

.stop-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
