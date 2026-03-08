<script setup lang="ts">
defineProps<{
  title: string;
}>();
</script>

<template>
  <header class="chat-header">
    <div class="header-left">
      <div class="header-icon">
        <span>AI</span>
        <div class="icon-glow"></div>
      </div>
      <div class="header-info">
        <h1>{{ title || "New Chat" }}</h1>
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
</style>
