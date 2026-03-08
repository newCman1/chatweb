<script setup lang="ts">
const props = defineProps<{
  title: string;
  showThinking: boolean;
}>();

const emit = defineEmits<{
  "update:showThinking": [value: boolean];
}>();

function onToggleThinking(event: Event) {
  const target = event.target as HTMLInputElement;
  emit("update:showThinking", target.checked);
}
</script>

<template>
  <header class="chat-header">
    <div class="header-left">
      <div class="header-icon">AI</div>
      <div class="header-info">
        <h1>{{ props.title }}</h1>
        <p class="subtitle">
          <span class="status-dot"></span>
          Assistant online
        </p>
      </div>
    </div>

    <div class="header-actions">
      <label class="thinking-toggle">
        <input type="checkbox" :checked="showThinking" @change="onToggleThinking" />
        Show thinking
      </label>
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
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
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
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.header-actions {
  display: flex;
  align-items: center;
}

.thinking-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 6px 10px;
  background: var(--bg-panel);
}

.thinking-toggle input {
  margin: 0;
  cursor: pointer;
}

.thinking-toggle:hover {
  border-color: var(--brand);
}
</style>
