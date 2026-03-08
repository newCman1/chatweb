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
  
  // 小于1小时显示分钟
  if (diff < 60 * 60 * 1000) {
    const mins = Math.floor(diff / (60 * 1000));
    return mins < 1 ? '刚刚' : `${mins}分钟前`;
  }
  
  // 小于24小时显示小时
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    return `${hours}小时前`;
  }
  
  // 小于7天显示星期几
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    return days[date.getDay()];
  }
  
  // 否则显示日期
  return `${date.getMonth() + 1}/${date.getDate()}`;
}
</script>

<template>
  <aside class="chat-sidebar">
    <div class="sidebar-header">
      <h2 class="sidebar-title">Chat Web</h2>
      <p class="sidebar-subtitle">AI 助手</p>
    </div>
    
    <button class="new-chat-btn" @click="$emit('create')">
      新建会话
    </button>
    
    <div class="conversations-section">
      <h3 class="section-title">
        <span class="section-icon">💬</span>
        会话列表
        <span class="conversation-count">{{ conversations.length }}</span>
      </h3>
      
      <ul class="conversation-list">
        <li 
          v-for="item in formattedConversations" 
          :key="item.id"
          class="conversation-item"
        >
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
        <span class="empty-icon">📝</span>
        <p>还没有会话</p>
        <p class="empty-hint">点击上方按钮开始新对话</p>
      </div>
    </div>
    
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">👤</div>
        <span class="user-name">访客用户</span>
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

.section-icon {
  font-size: 14px;
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

.conversation-icon {
  font-size: 14px;
  flex-shrink: 0;
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

.empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
  opacity: 0.5;
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

.sidebar-footer {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: var(--radius-md);
  background: var(--bg-soft);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--brand-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-main);
}
</style>
