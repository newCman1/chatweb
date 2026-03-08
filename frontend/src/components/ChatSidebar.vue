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
      <h2 class="sidebar-title">Chat Web</h2>
      <p class="sidebar-subtitle">Desktop Mode</p>
    </div>

    <button class="new-chat-btn" @click="$emit('create')">New chat</button>

    <div class="conversations-section">
      <h3 class="section-title">
        Conversations
        <span class="conversation-count">{{ conversations.length }}</span>
      </h3>

      <ul class="conversation-list">
        <li v-for="item in formattedConversations" :key="item.id" class="conversation-item">
          <button
            class="conversation-btn"
            :class="{ active: currentConversationId === item.id }"
            @click="$emit('select', item.id)"
          >
            <div class="conversation-content">
              <span class="title">{{ item.title }}</span>
            </div>
            <span class="time">{{ item.formattedTime }}</span>
          </button>
        </li>
      </ul>

      <div v-if="conversations.length === 0" class="empty-conversations">
        <p>No conversations yet.</p>
        <p class="empty-hint">Create one to start chatting.</p>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar-header {
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.sidebar-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  background: var(--brand-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sidebar-subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--text-tertiary);
}

.conversations-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.conversation-count {
  margin-left: auto;
  background: var(--bg-soft);
  color: var(--text-secondary);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}

.conversation-item {
  margin-bottom: 4px;
}

.conversation-content {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.empty-conversations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  color: var(--text-tertiary);
  text-align: center;
}

.empty-conversations p {
  margin: 0;
  font-size: 14px;
}

.empty-hint {
  font-size: 12px;
  margin-top: 4px;
  opacity: 0.7;
}
</style>
