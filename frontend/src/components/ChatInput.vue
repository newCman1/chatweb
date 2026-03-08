<script setup lang="ts">
import { computed, ref } from "vue";

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

const canSend = computed(() => !props.disabled && !props.isStreaming && draft.value.trim().length > 0);
const actionLabel = computed(() => (props.isStreaming ? "Stop" : "Send"));

function onSend() {
  const content = draft.value.trim();
  if (!content || props.disabled || props.isStreaming) return;
  emit("send", content);
  draft.value = "";
}

function onPrimaryAction() {
  if (props.isStreaming) {
    emit("stop");
    return;
  }
  onSend();
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
        <label class="thinking-toggle">
          <input type="checkbox" :checked="enableDeepThinking" @change="onToggleDeepThinking" />
          <span class="toggle-text">Deep thinking</span>
        </label>

        <div class="input-actions">
          <span class="input-hint"><kbd>Enter</kbd> send, <kbd>Shift</kbd>+<kbd>Enter</kbd> newline</span>
          <button
            class="primary-btn"
            :class="{ stop: isStreaming }"
            :disabled="isStreaming ? false : !canSend"
            @click="onPrimaryAction"
          >
            {{ actionLabel }}
          </button>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.chat-input-wrap {
  border-top: 1px solid var(--border);
  padding: 16px 20px 18px;
  background: var(--bg-panel);
}

.chat-input-container {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 14px;
  transition: all var(--transition-fast);
}

.chat-input-container:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--brand-soft);
}

.chat-input {
  width: 100%;
  min-height: 52px;
  max-height: 180px;
  padding: 12px 14px;
  border: none;
  border-radius: 14px 14px 0 0;
  background: transparent;
  font-size: 14px;
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
  border-top: 1px solid var(--border-light);
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.thinking-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  user-select: none;
}

.thinking-toggle input {
  margin: 0;
}

.input-actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.input-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  white-space: nowrap;
}

.input-hint kbd {
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 5px;
  font-family: var(--font-mono);
  font-size: 11px;
}

.primary-btn {
  border: none;
  border-radius: 10px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  color: #fff;
  background: var(--brand);
  transition: all var(--transition-fast);
  min-width: 72px;
}

.primary-btn:hover:not(:disabled) {
  background: var(--brand-strong);
}

.primary-btn.stop {
  background: var(--danger);
}

.primary-btn.stop:hover {
  background: #dc2626;
}

.primary-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
