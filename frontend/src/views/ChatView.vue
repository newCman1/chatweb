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

function onToggleThinking(messageId: string) {
  chatStore.toggleThinkingExpanded(messageId);
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
      <ChatHeader :title="title" />
      <MessageList
        :messages="messages"
        :thinking-expanded-by-message-id="chatStore.thinkingExpandedByMessageId"
        @toggle-thinking="onToggleThinking"
      />
      <p v-if="chatStore.errorText" class="error-toast">{{ chatStore.errorText }}</p>
      <ChatInput
        :disabled="!conversationStore.currentConversationId"
        :is-streaming="chatStore.isStreaming"
        :enable-deep-thinking="chatStore.enableDeepThinking"
        :enable-web-search="chatStore.enableWebSearch"
        :user-api-key="chatStore.userApiKey"
        :user-api-base-url="chatStore.userApiBaseUrl"
        :user-api-model="chatStore.userApiModel"
        :user-api-reasoning-model="chatStore.userApiReasoningModel"
        @send="onSend"
        @stop="chatStore.stop"
        @update:enable-deep-thinking="chatStore.setEnableDeepThinking"
        @update:enable-web-search="chatStore.setEnableWebSearch"
        @update:user-api-key="chatStore.setUserApiKey"
        @update:user-api-base-url="chatStore.setUserApiBaseUrl"
        @update:user-api-model="chatStore.setUserApiModel"
        @update:user-api-reasoning-model="chatStore.setUserApiReasoningModel"
      />
    </section>
  </main>
</template>
