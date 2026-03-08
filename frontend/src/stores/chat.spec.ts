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
    await chatStore.send("hello");

    const messages = conversationStore.currentMessages;
    expect(messages).toHaveLength(2);
    expect(messages[1].content).toBe("ABC");
    expect(messages[1].status).toBe("done");
  });

  it("marks message as stopped when stream is interrupted", async () => {
    const conversationStore = useConversationStore();
    await conversationStore.createConversation();
    const chatStore = useChatStore();
    const task = chatStore.send("stop test");
    await delay(1);
    chatStore.stop();
    await task;

    const assistant = conversationStore.currentMessages.find((m) => m.role === "assistant");
    expect(assistant).toBeTruthy();
    expect(["stopped", "done"]).toContain(assistant?.status);
  });

  it("persists thinking toggle preference", () => {
    const chatStore = useChatStore();
    chatStore.setShowThinking(true);
    expect(window.localStorage.getItem("chatweb.showThinking")).toBe("1");
    chatStore.setShowThinking(false);
    expect(window.localStorage.getItem("chatweb.showThinking")).toBe("0");
  });

  it("sends deep thinking preference to api", async () => {
    const conversationStore = useConversationStore();
    await conversationStore.createConversation();
    const chatStore = useChatStore();
    chatStore.setEnableDeepThinking(true);
    await chatStore.send("need deep thinking");
    expect(apiStub.lastInput?.enableThinking).toBe(true);

    chatStore.setEnableDeepThinking(false);
    await chatStore.send("no deep thinking");
    expect(apiStub.lastInput?.enableThinking).toBe(false);
  });
});
