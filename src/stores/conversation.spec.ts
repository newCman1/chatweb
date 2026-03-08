import { beforeEach, describe, expect, it } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useConversationStore } from "./conversation";
import { setChatApi } from "@/api/client";
import type { IChatApi, StreamReplyInput } from "@/api/chatApi";
import type { Conversation, Message, StreamChunk } from "@/types/chat";

class StubApi implements IChatApi {
  private conversations: Conversation[] = [];
  private messagesByConversation: Record<string, Message[]> = {};

  async listConversations() {
    return [...this.conversations];
  }

  async createConversation() {
    const now = new Date().toISOString();
    const item: Conversation = {
      id: crypto.randomUUID(),
      title: "New Chat",
      createdAt: now,
      updatedAt: now
    };
    this.conversations.unshift(item);
    this.messagesByConversation[item.id] = [];
    return item;
  }

  async listMessages(conversationId: string) {
    return [...(this.messagesByConversation[conversationId] ?? [])];
  }

  async *streamReply(_input: StreamReplyInput): AsyncGenerator<StreamChunk> {
    yield { delta: "noop", done: true };
  }

  abortStream(_conversationId: string): void {}

  seedConversation(conversation: Conversation, messages: Message[]) {
    this.conversations = [conversation, ...this.conversations];
    this.messagesByConversation[conversation.id] = messages;
  }
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
    await store.selectConversation(created.id);
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

  it("loads conversation history on init and select", async () => {
    const api = new StubApi();
    const now = new Date().toISOString();
    const c1: Conversation = {
      id: "c1",
      title: "First",
      createdAt: now,
      updatedAt: now
    };
    const c2: Conversation = {
      id: "c2",
      title: "Second",
      createdAt: now,
      updatedAt: now
    };
    api.seedConversation(c2, []);
    api.seedConversation(c1, [
      {
        id: "m1",
        conversationId: "c1",
        role: "assistant",
        content: "history",
        status: "done",
        createdAt: now
      }
    ]);
    setChatApi(api);

    const store = useConversationStore();
    await store.init();
    expect(store.currentConversationId).toBe("c1");
    expect(store.currentMessages).toHaveLength(1);
    await store.selectConversation("c2");
    expect(store.currentMessages).toHaveLength(0);
  });
});
