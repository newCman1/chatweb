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
    return `${Math.floor(diff / (60 * 60 * 1000))}h ago`;
  }
  return `${date.getMonth() + 1}/${date.getDate()}`;
}
</script>

<template>
  <aside class="chat-sidebar">
    <div class="sidebar-top">
      <h2>Chat Web</h2>
      <button class="new-chat-btn" @click="$emit('create')">New Chat</button>
    </div>

    <ul class="conversation-list">
      <li v-for="item in formattedConversations" :key="item.id">
        <button
          class="conversation-btn"
          :class="{ active: currentConversationId === item.id }"
          @click="$emit('select', item.id)"
        >
          <span class="title">{{ item.title }}</span>
          <span class="time">{{ item.formattedTime }}</span>
        </button>
      </li>
    </ul>

    <p v-if="conversations.length === 0" class="empty-text">No conversation yet.</p>
  </aside>
</template>

<style scoped>
.chat-sidebar {
  background: linear-gradient(180deg, #f8fbff 0%, #f1f5f9 100%);
  border: 1px solid #d4deea;
  border-radius: 14px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow: hidden;
}

.sidebar-top {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-top h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
}

.new-chat-btn {
  border: none;
  border-radius: 10px;
  background: var(--brand);
  color: #fff;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.new-chat-btn:hover {
  background: var(--brand-strong);
}

.conversation-list {
  list-style: none;
  padding: 8px;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  flex: 1;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid #d9e2ee;
  border-radius: 12px;
}

.conversation-btn {
  width: 100%;
  border: 1px solid #dce4ef;
  border-radius: 10px;
  padding: 10px 12px;
  background: #fff;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast),
    box-shadow var(--transition-fast), transform var(--transition-fast);
}

.conversation-btn:hover {
  background: #f8fbff;
  border-color: #c7d7ea;
  box-shadow: 0 1px 0 rgba(148, 163, 184, 0.16);
  transform: translateY(-1px);
}

.conversation-btn.active {
  background: #eaf3ff;
  border-color: #8eb9ff;
  box-shadow: inset 0 0 0 1px #9ec5ff;
}

.title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time {
  font-size: 11px;
  color: #64748b;
}

.empty-text {
  margin: 0;
  font-size: 12px;
  color: var(--text-tertiary);
  text-align: center;
}
</style>
