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

function insertCodeBlock() {
  draft.value += "\n```\n\n```";
}

function insertList() {
  draft.value += "\n- ";
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
        <div class="toolbar-left">
          <button class="toolbar-btn" title="Insert code block" @click="insertCodeBlock">
            <span class="btn-icon">{ }</span>
          </button>
          <button class="toolbar-btn" title="Insert list" @click="insertList">
            <span class="btn-icon">☰</span>
          </button>
        </div>
        <span class="input-hint">
          <kbd>Enter</kbd> to send · <kbd>Shift</kbd> + <kbd>Enter</kbd> for new line
        </span>
      </div>
    </div>
    <div class="chat-actions">
      <button 
        class="stop-btn" 
        :disabled="!isStreaming" 
        @click="$emit('stop')"
      >
        <span class="btn-icon">⏹</span>
        Stop
      </button>
      <button 
        class="send-btn" 
        :disabled="disabled || isStreaming || !draft.trim()" 
        @click="onSend"
      >
        <span class="btn-icon">➤</span>
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
  position: relative;
}

.chat-input-wrap::before {
  content: '';
  position: absolute;
  top: 0;
  left: 24px;
  right: 24px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
}

.chat-input-container {
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 6px;
  transition: all var(--transition-fast);
  margin-bottom: 12px;
}

.chat-input-container:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 4px var(--brand-soft), var(--shadow-glow);
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
  font-style: italic;
}

.chat-input-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-top: 1px solid var(--border-light);
  margin-top: 6px;
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.toolbar-btn {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.toolbar-btn:hover {
  background: var(--bg-panel);
  border-color: var(--brand);
  color: var(--brand);
}

.btn-icon {
  font-weight: 600;
}

.input-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.input-hint kbd {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2px 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
}

.chat-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.chat-actions button {
  border: none;
  border-radius: var(--radius-md);
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all var(--transition-fast);
}

.send-btn {
  background: var(--brand-gradient);
  color: #fff;
  box-shadow: var(--shadow-sm);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md), var(--shadow-glow);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stop-btn {
  background: var(--danger-soft);
  color: var(--danger);
  border: 1px solid transparent;
}

.stop-btn:hover:not(:disabled) {
  background: var(--danger);
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.stop-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
