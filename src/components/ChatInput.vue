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
        placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
        :disabled="disabled"
        rows="1"
        @keydown="onKeydown"
      />
      
      <div class="chat-input-toolbar">
        <div class="toolbar-left">
          <button 
            class="toolbar-btn" 
            title="插入代码块"
            @click="insertCodeBlock"
            :disabled="disabled"
          >
            <span>{}</span>
          </button>
          <button 
            class="toolbar-btn" 
            title="插入列表"
            @click="insertList"
            :disabled="disabled"
          >
            <span>☰</span>
          </button>
        </div>
        
        <div class="toolbar-right">
          <span class="input-hint">Enter 发送 · Shift+Enter 换行</span>
        </div>
      </div>
    </div>
    
    <div class="chat-actions">
      <button 
        v-if="isStreaming"
        class="stop-btn" 
        @click="$emit('stop')"
      >
        <span class="btn-icon">⏹</span>
        停止生成
      </button>
      <button 
        v-else
        class="send-btn" 
        :disabled="disabled || !draft.trim()"
        @click="onSend"
      >
        <span class="btn-icon">➤</span>
        发送
      </button>
    </div>
  </footer>
</template>

<style scoped>
.chat-input-wrap {
  border-top: 1px solid var(--border);
  padding: 16px 24px 20px;
  background: var(--bg-panel);
}

.chat-input-container {
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 4px;
  transition: all var(--transition-fast);
}

.chat-input-container:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--brand-soft);
}

.chat-input {
  width: 100%;
  min-height: 52px;
  max-height: 200px;
  padding: 12px 16px;
  border: none;
  border-radius: var(--radius-lg);
  background: transparent;
  font-size: 15px;
  line-height: 1.5;
  color: var(--text-main);
  resize: none;
  outline: none;
  font-family: inherit;
}

.chat-input::placeholder {
  color: var(--text-tertiary);
}

.chat-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chat-input-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-top: 1px solid var(--border-light);
  margin-top: 4px;
}

.toolbar-left {
  display: flex;
  gap: 4px;
}

.toolbar-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  transition: all var(--transition-fast);
}

.toolbar-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-main);
}

.toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.input-hint {
  font-size: 12px;
  color: var(--text-tertiary);
}

.chat-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
  gap: 8px;
}

.chat-actions button {
  border: none;
  border-radius: var(--radius-md);
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all var(--transition-fast);
}

.btn-icon {
  font-size: 12px;
}

.send-btn {
  background: var(--brand-gradient);
  color: #fff;
  box-shadow: var(--shadow-sm);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stop-btn {
  background: var(--danger-soft);
  color: var(--danger);
}

.stop-btn:hover {
  background: var(--danger);
  color: white;
}
</style>
