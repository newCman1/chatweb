<script setup lang="ts">
defineProps<{
  title: string;
}>();
</script>

<template>
  <header class="chat-header">
    <h1>{{ title || "New Chat" }}</h1>
    <p class="subtitle">
      <span class="status-dot"></span>
      Assistant online
    </p>
  </header>
</template>

<style scoped>
.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
}

.chat-header h1 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--text-main);
  max-width: 70%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.subtitle {
  margin: 0;
  font-size: 12px;
  color: var(--text-tertiary);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--success);
}
</style>
