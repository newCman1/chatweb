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
    formattedTime: new Date(c.updatedAt).toLocaleTimeString()
  }))
);
</script>

<template>
  <aside class="chat-sidebar">
    <button class="new-chat-btn" @click="$emit('create')">+ 新建会话</button>
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
  </aside>
</template>
