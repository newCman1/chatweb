import { beforeEach, describe, expect, it } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useConversationStore } from "./conversation";
import { setChatApi } from "@/api/client";
import type { IChatApi, StreamReplyInput } from "@/api/chatApi";
import type { Conversation, StreamChunk } from "@/types/chat";

class StubApi implements IChatApi {
  private conversations: Conversation[] = [];

  async listConversations() {
    return [...this.conversations];
  }

  async createConversation() {
    const now = new Date().toISOString();
    const item: Conversation = {
      id: crypto.randomUUID(),
      title: "新会话",
      createdAt: now,
      updatedAt: now
    };
    this.conversations.unshift(item);
    return item;
  }

  async *streamReply(_input: StreamReplyInput): AsyncGenerator<StreamChunk> {
    yield { delta: "noop", done: true };
  }

  abortStream(_conversationId: string): void {}
}

describe("conversation store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    setChatApi(new StubApi());
  });

  it("creates and switches conversation", async () => {
    const store = useConversationStore();
    const created = await store.createConversation();
    expect(store.currentConversationId).toBe(created.id);
    expect(store.conversations.length).toBe(1);
    store.selectConversation(created.id);
    expect(store.currentConversationId).toBe(created.id);
  });

  it("isolates messages between conversations", async () => {
    const store = useConversationStore();
    const first = await store.createConversation();
    store.addMessage({
      id: "m1",
      conversationId: first.id,
      role: "user",
      content: "hello",
      status: "done",
      createdAt: new Date().toISOString()
    });

    const second = await store.createConversation();
    expect(store.messagesByConversation[first.id]).toHaveLength(1);
    expect(store.messagesByConversation[second.id]).toHaveLength(0);
  });
});
