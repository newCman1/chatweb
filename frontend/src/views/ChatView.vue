<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import ChatSidebar from "@/components/ChatSidebar.vue";
import ChatHeader from "@/components/ChatHeader.vue";
import MessageList from "@/components/MessageList.vue";
import ChatInput from "@/components/ChatInput.vue";
import { useConversationStore } from "@/stores/conversation";
import { useChatStore } from "@/stores/chat";

const conversationStore = useConversationStore();
const chatStore = useChatStore();

const title = computed(() => conversationStore.currentConversation?.title ?? "New Chat");
const messages = computed(() => conversationStore.currentMessages);

async function onCreateConversation() {
  await conversationStore.createConversation();
}

function onSelectConversation(conversationId: string) {
  void conversationStore.selectConversation(conversationId);
}

async function onSend(content: string) {
  await chatStore.send(content);
}

watch(
  () => chatStore.errorText,
  (error) => {
    if (error) {
      setTimeout(() => {
        chatStore.errorText = null;
      }, 5000);
    }
  }
);

onMounted(async () => {
  await conversationStore.init();
  if (!conversationStore.currentConversationId) {
    await conversationStore.createConversation();
  }
});
</script>

<template>
  <main class="desktop-shell">
    <ChatSidebar
      :conversations="conversationStore.conversations"
      :current-conversation-id="conversationStore.currentConversationId"
      @create="onCreateConversation"
      @select="onSelectConversation"
    />

    <section class="chat-main">
      <ChatHeader
        :title="title"
        :show-thinking="chatStore.showThinking"
        :enable-deep-thinking="chatStore.enableDeepThinking"
        @update:show-thinking="chatStore.setShowThinking"
        @update:enable-deep-thinking="chatStore.setEnableDeepThinking"
      />
      <MessageList :messages="messages" :show-thinking="chatStore.showThinking" />
      <p v-if="chatStore.errorText" class="error-toast">{{ chatStore.errorText }}</p>
      <ChatInput
        :disabled="!conversationStore.currentConversationId"
        :is-streaming="chatStore.isStreaming"
        @send="onSend"
        @stop="chatStore.stop"
      />
    </section>
  </main>
</template>
