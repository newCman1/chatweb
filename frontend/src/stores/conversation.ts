import { defineStore } from "pinia";
import type { Conversation, Message } from "@/types/chat";
import { chatApi } from "@/api/client";
import { logger } from "@/utils/logger";

interface ConversationState {
  conversations: Conversation[];
  currentConversationId: string | null;
  messagesByConversation: Record<string, Message[]>;
}

const now = () => new Date().toISOString();

function titleFromMessage(content: string): string {
  const cleaned = content.replace(/\s+/g, " ").trim();
  return cleaned.slice(0, 24) || "New Chat";
}

export const useConversationStore = defineStore("conversation", {
  state: (): ConversationState => ({
    conversations: [],
    currentConversationId: null,
    messagesByConversation: {}
  }),
  getters: {
    currentConversation(state): Conversation | null {
      return state.conversations.find((c) => c.id === state.currentConversationId) ?? null;
    },
    currentMessages(state): Message[] {
      if (!state.currentConversationId) return [];
      return state.messagesByConversation[state.currentConversationId] ?? [];
    }
  },
  actions: {
    async init() {
      try {
        const items = await chatApi.listConversations();
        this.conversations = items;
        logger.info("conversation.init", { total: items.length });
        if (!this.currentConversationId && items.length > 0) {
          this.currentConversationId = items[0].id;
          await this.ensureMessagesLoaded(items[0].id);
        }
      } catch (err) {
        logger.error("conversation.init.failed", {
          error: err instanceof Error ? err.message : "unknown"
        });
        this.conversations = [];
      }
    },
    async createConversation(): Promise<Conversation> {
      const conversation = await chatApi.createConversation();
      this.conversations.unshift(conversation);
      this.messagesByConversation[conversation.id] = [];
      this.currentConversationId = conversation.id;
      logger.info("conversation.created", { conversationId: conversation.id });
      return conversation;
    },
    async selectConversation(conversationId: string) {
      this.currentConversationId = conversationId;
      await this.ensureMessagesLoaded(conversationId);
      logger.debug("conversation.selected", { conversationId });
    },
    addMessage(message: Message) {
      if (!this.messagesByConversation[message.conversationId]) {
        this.messagesByConversation[message.conversationId] = [];
      }
      this.messagesByConversation[message.conversationId].push(message);
      const conversation = this.conversations.find((c) => c.id === message.conversationId);
      if (conversation) {
        conversation.updatedAt = now();
        if (message.role === "user" && conversation.title === "New Chat") {
          conversation.title = titleFromMessage(message.content);
        }
      }
      logger.debug("conversation.message.added", {
        conversationId: message.conversationId,
        messageId: message.id,
        role: message.role
      });
    },
    patchMessage(conversationId: string, messageId: string, patch: Partial<Message>) {
      const messages = this.messagesByConversation[conversationId] ?? [];
      const target = messages.find((msg) => msg.id === messageId);
      if (target) {
        Object.assign(target, patch);
      }
    },
    async ensureMessagesLoaded(conversationId: string) {
      if (this.messagesByConversation[conversationId]) return;
      try {
        const messages = await chatApi.listMessages(conversationId);
        this.messagesByConversation[conversationId] = messages;
      } catch (err) {
        logger.error("conversation.messages.load.failed", {
          conversationId,
          error: err instanceof Error ? err.message : "unknown"
        });
        this.messagesByConversation[conversationId] = [];
      }
    }
  }
});
