import { defineStore } from "pinia";
import { chatApi } from "@/api/client";
import { useConversationStore } from "./conversation";
import type { Message } from "@/types/chat";
import { logger } from "@/utils/logger";

interface ChatState {
  isStreaming: boolean;
  activeConversationId: string | null;
  activeAssistantMessageId: string | null;
  activeAbortController: AbortController | null;
  errorText: string | null;
  showThinking: boolean;
}

const uid = () => crypto.randomUUID();
const now = () => new Date().toISOString();
const THINKING_PREF_KEY = "chatweb.showThinking";

function loadThinkingPreference(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(THINKING_PREF_KEY) === "1";
}

export const useChatStore = defineStore("chat", {
  state: (): ChatState => ({
    isStreaming: false,
    activeConversationId: null,
    activeAssistantMessageId: null,
    activeAbortController: null,
    errorText: null,
    showThinking: loadThinkingPreference()
  }),
  actions: {
    async send(content: string) {
      const trimmed = content.trim();
      if (!trimmed || this.isStreaming) return;

      const conversationStore = useConversationStore();
      if (!conversationStore.currentConversationId) {
        await conversationStore.createConversation();
      }

      const conversationId = conversationStore.currentConversationId;
      if (!conversationId) return;

      this.errorText = null;
      logger.info("chat.send", { conversationId, contentLength: trimmed.length });
      const userMessage: Message = {
        id: uid(),
        conversationId,
        role: "user",
        content: trimmed,
        status: "done",
        createdAt: now()
      };
      conversationStore.addMessage(userMessage);

      const assistantMessageId = uid();
      const assistantMessage: Message = {
        id: assistantMessageId,
        conversationId,
        role: "assistant",
        content: "",
        thinking: "",
        status: "streaming",
        createdAt: now()
      };
      conversationStore.addMessage(assistantMessage);

      this.isStreaming = true;
      this.activeConversationId = conversationId;
      this.activeAssistantMessageId = assistantMessageId;
      this.activeAbortController = new AbortController();
      logger.info("chat.stream.start", { conversationId, assistantMessageId });

      try {
        const stream = chatApi.streamReply({
          conversationId,
          messages: conversationStore.messagesByConversation[conversationId],
          signal: this.activeAbortController.signal
        });
        for await (const chunk of stream) {
          if (chunk.delta) {
            const current = conversationStore.messagesByConversation[conversationId].find(
              (m) => m.id === assistantMessageId
            );
            const next = `${current?.content ?? ""}${chunk.delta}`;
            conversationStore.patchMessage(conversationId, assistantMessageId, {
              content: next
            });
          }
          if (chunk.thinkingDelta) {
            const current = conversationStore.messagesByConversation[conversationId].find(
              (m) => m.id === assistantMessageId
            );
            const nextThinking = `${current?.thinking ?? ""}${chunk.thinkingDelta}`;
            conversationStore.patchMessage(conversationId, assistantMessageId, {
              thinking: nextThinking
            });
          }
          if (chunk.done) {
            conversationStore.patchMessage(conversationId, assistantMessageId, {
              status: "done"
            });
            logger.info("chat.stream.done", { conversationId, assistantMessageId });
          }
        }
      } catch (err) {
        const isAbort = err instanceof Error && err.name === "AbortError";
        conversationStore.patchMessage(conversationId, assistantMessageId, {
          status: isAbort ? "stopped" : "error"
        });
        if (!isAbort) {
          this.errorText = "Generation failed, please retry.";
          logger.error("chat.stream.error", {
            conversationId,
            assistantMessageId,
            error: err instanceof Error ? err.message : "unknown"
          });
        } else {
          logger.warn("chat.stream.stopped", { conversationId, assistantMessageId });
        }
      } finally {
        this.isStreaming = false;
        this.activeConversationId = null;
        this.activeAssistantMessageId = null;
        this.activeAbortController = null;
      }
    },
    stop() {
      if (!this.isStreaming || !this.activeConversationId) return;
      logger.warn("chat.stop.requested", { conversationId: this.activeConversationId });
      this.activeAbortController?.abort();
      chatApi.abortStream(this.activeConversationId);
    },
    setShowThinking(show: boolean) {
      this.showThinking = show;
      if (typeof window !== "undefined") {
        window.localStorage.setItem(THINKING_PREF_KEY, show ? "1" : "0");
      }
    }
  }
});
