<script setup lang="ts">
const props = defineProps<{
  title: string;
  showThinking: boolean;
  enableDeepThinking: boolean;
}>();

const emit = defineEmits<{
  "update:showThinking": [value: boolean];
  "update:enableDeepThinking": [value: boolean];
}>();

function onToggleThinking(event: Event) {
  const target = event.target as HTMLInputElement;
  emit("update:showThinking", target.checked);
}

function onToggleDeepThinking(event: Event) {
  const target = event.target as HTMLInputElement;
  emit("update:enableDeepThinking", target.checked);
}
</script>

<template>
  <header class="chat-header">
    <div class="header-left">
      <div class="header-icon">
        <span>AI</span>
        <div class="icon-glow"></div>
      </div>
      <div class="header-info">
        <h1>{{ props.title || "New Chat" }}</h1>
        <p class="subtitle">
          <span class="status-dot"></span>
          <span class="status-text">Assistant is online</span>
        </p>
      </div>
    </div>

    <div class="header-actions">
      <button class="header-btn" title="Clear chat">
        <span class="btn-icon">X</span>
        <span class="btn-text">Clear</span>
      </button>

      <label class="thinking-toggle">
        <input type="checkbox" :checked="showThinking" @change="onToggleThinking" />
        <span class="toggle-slider"></span>
        <span class="toggle-text">Show reasoning</span>
      </label>

      <label class="thinking-toggle deep-thinking-toggle">
        <input type="checkbox" :checked="enableDeepThinking" @change="onToggleDeepThinking" />
        <span class="toggle-slider"></span>
        <span class="toggle-text">Enable deep thinking</span>
      </label>
    </div>
  </header>
</template>

<style scoped>
.chat-header {
  padding: 18px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, var(--bg-panel) 0%, var(--bg-soft) 100%);
  position: relative;
}

.chat-header::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 24px;
  right: 24px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background: var(--brand-gradient);
  color: #fff;
  font-size: 14px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.icon-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.3), transparent);
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.header-info h1 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--text-main);
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.3px;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  background: var(--success);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
  box-shadow: 0 0 8px var(--success);
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(0.9);
  }
}

.status-text {
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-btn {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 8px 14px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.header-btn:hover {
  background: var(--bg-soft);
  border-color: var(--danger);
  color: var(--danger);
}

.btn-icon {
  font-size: 14px;
}

.thinking-toggle {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--text-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 8px 14px;
  background: var(--bg-panel);
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
  position: relative;
}

.thinking-toggle:hover {
  border-color: var(--brand);
}

.thinking-toggle input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  width: 36px;
  height: 20px;
  background: var(--bg-soft);
  border-radius: 999px;
  position: relative;
  transition: all var(--transition-fast);
  border: 1px solid var(--border);
}

.toggle-slider::before {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  background: white;
  border-radius: 50%;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.thinking-toggle input:checked + .toggle-slider {
  background: var(--brand);
  border-color: var(--brand);
}

.thinking-toggle input:checked + .toggle-slider::before {
  transform: translateX(16px);
}

.toggle-text {
  font-weight: 500;
}

.deep-thinking-toggle input:checked + .toggle-slider {
  background: var(--success);
  border-color: var(--success);
}
</style>
