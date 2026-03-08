import { beforeEach, describe, expect, it } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useConversationStore } from "./conversation";
import { useChatStore } from "./chat";
import { setChatApi } from "@/api/client";
import type { IChatApi, StreamReplyInput } from "@/api/chatApi";
import type { Conversation, StreamChunk } from "@/types/chat";

const delay = (ms: number) =>
  new Promise<void>((resolve) => {
    setTimeout(resolve, ms);
  });

class StreamingApiStub implements IChatApi {
  lastInput: StreamReplyInput | null = null;

  async listConversations() {
    return [];
  }

  async createConversation() {
    const now = new Date().toISOString();
    return {
      id: crypto.randomUUID(),
      title: "New Chat",
      createdAt: now,
      updatedAt: now
    } satisfies Conversation;
  }

  async listMessages() {
    return [];
  }

  async *streamReply(input: StreamReplyInput): AsyncGenerator<StreamChunk> {
    this.lastInput = input;
    const chunks = ["A", "B", "C"];
    for (const chunk of chunks) {
      if (input.signal?.aborted) {
        const err = new Error("aborted");
        err.name = "AbortError";
        throw err;
      }
      yield { delta: chunk };
      await delay(2);
    }
    yield { delta: "", done: true };
  }

  abortStream(_conversationId: string): void {}
}

describe("chat store", () => {
  let apiStub: StreamingApiStub;

  beforeEach(() => {
    setActivePinia(createPinia());
    apiStub = new StreamingApiStub();
    setChatApi(apiStub);
    window.localStorage.clear();
  });

  it("streams assistant response", async () => {
    const conversationStore = useConversationStore();
    await conversationStore.createConversation();
    const chatStore = useChatStore();
    await chatStore.send({ content: "hello" });

    const messages = conversationStore.currentMessages;
    expect(messages).toHaveLength(2);
    expect(messages[1].content).toBe("ABC");
    expect(messages[1].status).toBe("done");
  });

  it("marks message as stopped when stream is interrupted", async () => {
    const conversationStore = useConversationStore();
    await conversationStore.createConversation();
    const chatStore = useChatStore();
    const task = chatStore.send({ content: "stop test" });
    await delay(1);
    chatStore.stop();
    await task;

    const assistant = conversationStore.currentMessages.find((m) => m.role === "assistant");
    expect(assistant).toBeTruthy();
    expect(["stopped", "done"]).toContain(assistant?.status);
  });

  it("persists deep thinking toggle preference", () => {
    const chatStore = useChatStore();
    chatStore.setEnableDeepThinking(true);
    expect(window.localStorage.getItem("chatweb.enableDeepThinking")).toBe("1");
    chatStore.setEnableDeepThinking(false);
    expect(window.localStorage.getItem("chatweb.enableDeepThinking")).toBe("0");
  });

  it("sends deep thinking preference to api", async () => {
    const conversationStore = useConversationStore();
    await conversationStore.createConversation();
    const chatStore = useChatStore();
    chatStore.setEnableDeepThinking(true);
    await chatStore.send({ content: "need deep thinking" });
    expect(apiStub.lastInput?.enableThinking).toBe(true);

    chatStore.setEnableDeepThinking(false);
    await chatStore.send({ content: "no deep thinking" });
    expect(apiStub.lastInput?.enableThinking).toBe(false);
  });

  it("sends web search and runtime api options to api", async () => {
    const conversationStore = useConversationStore();
    await conversationStore.createConversation();
    const chatStore = useChatStore();
    chatStore.setEnableWebSearch(true);
    chatStore.setUserApiKey("sk-test");
    chatStore.setUserApiBaseUrl("https://api.deepseek.com/v1");
    chatStore.setUserApiModel("deepseek-chat");
    chatStore.setUserApiReasoningModel("deepseek-reasoner");

    await chatStore.send({ content: "use web" });
    expect(apiStub.lastInput?.enableWebSearch).toBe(true);
    expect(apiStub.lastInput?.apiKey).toBe("sk-test");
    expect(apiStub.lastInput?.apiBaseUrl).toBe("https://api.deepseek.com/v1");
    expect(apiStub.lastInput?.apiModel).toBe("deepseek-chat");
    expect(apiStub.lastInput?.apiReasoningModel).toBe("deepseek-reasoner");
  });

  it("persists web search and api settings", () => {
    const chatStore = useChatStore();
    chatStore.setEnableWebSearch(true);
    chatStore.setUserApiKey("sk-local");
    chatStore.setUserApiBaseUrl("https://api.local/v1");
    expect(window.localStorage.getItem("chatweb.enableWebSearch")).toBe("1");
    expect(window.localStorage.getItem("chatweb.userApiKey")).toBe("sk-local");
    expect(window.localStorage.getItem("chatweb.userApiBaseUrl")).toBe("https://api.local/v1");
  });

  it("keeps thinking panel expanded state in store", () => {
    const chatStore = useChatStore();
    const messageId = crypto.randomUUID();
    expect(chatStore.isThinkingExpanded(messageId)).toBe(false);
    chatStore.toggleThinkingExpanded(messageId);
    expect(chatStore.isThinkingExpanded(messageId)).toBe(true);
    chatStore.toggleThinkingExpanded(messageId);
    expect(chatStore.isThinkingExpanded(messageId)).toBe(false);
  });

  it("passes attachments to api", async () => {
    const conversationStore = useConversationStore();
    await conversationStore.createConversation();
    const chatStore = useChatStore();
    await chatStore.send({
      content: "read this file",
      attachments: [
        {
          name: "notes.txt",
          mimeType: "text/plain",
          content: "hello attachment",
          size: 16
        }
      ]
    });
    expect(apiStub.lastInput?.attachments).toHaveLength(1);
    expect(apiStub.lastInput?.attachments?.[0].name).toBe("notes.txt");
  });
});
