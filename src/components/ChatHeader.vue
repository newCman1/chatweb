<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  title: string;
}>();

const displayTitle = computed(() => {
  if (props.title === "新会话") {
    return "新对话";
  }
  return props.title;
});
</script>

<template>
  <header class="chat-header">
    <div class="header-left">
      <div class="header-icon">💬</div>
      <div class="header-info">
        <h1>{{ displayTitle }}</h1>
        <p class="subtitle">
          <span class="status-dot"></span>
          AI 助手在线
        </p>
      </div>
    </div>
    
    <div class="header-actions">
      <button class="header-btn" title="清空对话">
        <span>🗑️</span>
      </button>
      <button class="header-btn" title="设置">
        <span>⚙️</span>
      </button>
    </div>
  </header>
</template>

<style scoped>
.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(to right, var(--bg-panel), var(--bg-soft));
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--brand-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: var(--shadow-sm);
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.header-info h1 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: var(--success);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-panel);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all var(--transition-fast);
}

.header-btn:hover {
  background: var(--bg-soft);
  border-color: var(--brand);
  transform: translateY(-1px);
}
</style>
