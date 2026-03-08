<script setup lang="ts">
import type { Conversation } from "@/types/chat";
import { computed } from "vue";

const props = defineProps<{
  conversations: Conversation[];
  currentConversationId: string | null;
}>();

defineEmits<{
  create: [];
  select: [conversationId: string];
}>();

const formattedConversations = computed(() =>
  props.conversations.map((c) => ({
    ...c,
    formattedTime: formatTime(c.updatedAt)
  }))
);

function formatTime(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  if (diff < 60 * 60 * 1000) {
    const mins = Math.floor(diff / (60 * 1000));
    return mins < 1 ? "just now" : `${mins}m ago`;
  }

  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    return `${hours}h ago`;
  }

  if (diff < 7 * 24 * 60 * 60 * 1000) {
    return date.toLocaleDateString("en-US", { weekday: "short" });
  }

  return `${date.getMonth() + 1}/${date.getDate()}`;
}
</script>

<template>
  <aside class="chat-sidebar">
    <div class="sidebar-header">
      <div class="brand">
        <div class="brand-icon">🤖</div>
        <div class="brand-text">
          <h2 class="brand-title">Chat AI</h2>
          <p class="brand-subtitle">Desktop Mode</p>
        </div>
      </div>
    </div>

    <button class="new-chat-btn" @click="$emit('create')">
      <span class="btn-icon">+</span>
      <span class="btn-text">New Chat</span>
    </button>

    <div class="conversations-section">
      <div class="section-header">
        <h3 class="section-title">
          <span class="section-icon">💬</span>
          Conversations
        </h3>
        <span class="conversation-count">{{ conversations.length }}</span>
      </div>

      <ul class="conversation-list">
        <li v-for="item in formattedConversations" :key="item.id" class="conversation-item">
          <button
            class="conversation-btn"
            :class="{ active: currentConversationId === item.id }"
            @click="$emit('select', item.id)"
          >
            <div class="conversation-content">
              <span class="conversation-icon">💭</span>
              <span class="title">{{ item.title }}</span>
            </div>
            <span class="time">{{ item.formattedTime }}</span>
          </button>
        </li>
      </ul>

      <div v-if="conversations.length === 0" class="empty-conversations">
        <div class="empty-icon">📝</div>
        <p class="empty-title">No conversations yet</p>
        <p class="empty-hint">Click "New Chat" to start</p>
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">👤</div>
        <span class="user-name">User</span>
      </div>
      <button class="settings-btn" title="Settings">
        <span>⚙️</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar-header {
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  width: 44px;
  height: 44px;
  background: var(--brand-gradient);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  box-shadow: var(--shadow-md);
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.brand-title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  background: var(--brand-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.brand-subtitle {
  margin: 0;
  font-size: 12px;
  color: var(--text-tertiary);
  font-weight: 500;
}

.new-chat-btn {
  border: none;
  border-radius: var(--radius-md);
  background: var(--brand-gradient);
  color: #fff;
  padding: 14px 18px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}

.new-chat-btn::before {
  content: "";
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}

.new-chat-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.new-chat-btn:hover::before {
  left: 100%;
}

.new-chat-btn:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: 18px;
  font-weight: 300;
}

.conversations-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.section-icon {
  font-size: 14px;
}

.conversation-count {
  background: var(--bg-soft);
  color: var(--text-secondary);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  min-width: 24px;
  text-align: center;
}

.conversation-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  flex: 1;
}

.conversation-item {
  margin: 0;
}

.conversation-btn {
  width: 100%;
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  padding: 12px 14px;
  background: transparent;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
}

.conversation-btn:hover {
  background: var(--bg-soft);
  border-color: var(--border);
  transform: translateX(4px);
}

.conversation-btn.active {
  background: var(--brand-soft);
  border-color: var(--brand);
  box-shadow: 0 0 0 1px var(--brand-soft);
}

.conversation-btn.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--brand);
  border-radius: 0 2px 2px 0;
}

.conversation-content {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
}

.conversation-icon {
  font-size: 14px;
  opacity: 0.6;
  flex-shrink: 0;
}

.title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-main);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time {
  font-size: 11px;
  color: var(--text-tertiary);
  padding-left: 24px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.time::before {
  content: '🕐';
  font-size: 9px;
}

.empty-conversations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-title {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.empty-hint {
  font-size: 12px;
  margin: 0;
  color: var(--text-tertiary);
}

.sidebar-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: var(--bg-soft);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  border: 2px solid var(--border);
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-main);
}

.settings-btn {
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.settings-btn:hover {
  background: var(--bg-soft);
  border-color: var(--brand);
  transform: rotate(30deg);
}
</style>
