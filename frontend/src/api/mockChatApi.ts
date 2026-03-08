import type { Conversation, Message, StreamChunk } from "@/types/chat";
import type { IChatApi, StreamReplyInput } from "./chatApi";
import { logger } from "@/utils/logger";

const wait = (ms: number) =>
  new Promise<void>((resolve) => {
    setTimeout(resolve, ms);
  });

const uid = () => crypto.randomUUID();

function splitToChunks(text: string): string[] {
  return text.split(/(\s+)/).filter((part) => part.length > 0);
}

function buildAssistantReply(userText: string): string {
  const base =
    "This is a frontend mock streaming response. Replace only the API adapter after backend integration.";
  const tips = "Next step: wire real SSE endpoint and server-side persistence.";
  return `You said: ${userText}\n\n${base}\n${tips}`;
}

function buildThinkingText(userText: string): string {
  return `Understanding your request: "${userText.slice(0, 60)}".\nPlanning a concise and practical answer.\nGenerating final response.`;
}

export class MockChatApi implements IChatApi {
  private conversations: Conversation[] = [];
  private messagesByConversation: Record<string, Message[]> = {};
  private activeAbortMap = new Map<string, AbortController>();
  private tokenDelayMs: number;

  constructor(options?: { tokenDelayMs?: number }) {
    this.tokenDelayMs = options?.tokenDelayMs ?? 45;
  }

  async listConversations(): Promise<Conversation[]> {
    logger.debug("api.listConversations");
    return [...this.conversations];
  }

  async createConversation(): Promise<Conversation> {
    const now = new Date().toISOString();
    const conversation: Conversation = {
      id: uid(),
      title: "New Chat",
      createdAt: now,
      updatedAt: now
    };
    this.conversations.unshift(conversation);
    this.messagesByConversation[conversation.id] = [];
    logger.info("api.createConversation", { conversationId: conversation.id });
    return conversation;
  }

  async listMessages(conversationId: string): Promise<Message[]> {
    return [...(this.messagesByConversation[conversationId] ?? [])];
  }

  async *streamReply(input: StreamReplyInput): AsyncGenerator<StreamChunk> {
    const external = input.signal;
    const internal = new AbortController();
    this.activeAbortMap.set(input.conversationId, internal);
    logger.info("api.stream.start", { conversationId: input.conversationId });

    const userMessage = [...input.messages].reverse().find((m) => m.role === "user");
    if (userMessage) {
      this.pushMessage(input.conversationId, userMessage);
    }

    const fullText = buildAssistantReply(userMessage?.content ?? "");
    const thinkingText = buildThinkingText(userMessage?.content ?? "");
    const thinkingChunks = splitToChunks(thinkingText);
    const chunks = splitToChunks(fullText);

    try {
      for (const chunk of thinkingChunks) {
        if (external?.aborted || internal.signal.aborted) {
          logger.warn("api.stream.aborted", { conversationId: input.conversationId });
          const err = new Error("Stream aborted");
          err.name = "AbortError";
          throw err;
        }
        yield { delta: "", thinkingDelta: chunk };
        await wait(this.tokenDelayMs);
      }
      for (const chunk of chunks) {
        if (external?.aborted || internal.signal.aborted) {
          logger.warn("api.stream.aborted", { conversationId: input.conversationId });
          const err = new Error("Stream aborted");
          err.name = "AbortError";
          throw err;
        }
        yield { delta: chunk };
        await wait(this.tokenDelayMs);
      }
      logger.info("api.stream.done", { conversationId: input.conversationId });
      yield { delta: "", done: true };
    } finally {
      this.activeAbortMap.delete(input.conversationId);
    }
  }

  abortStream(conversationId: string): void {
    const controller = this.activeAbortMap.get(conversationId);
    if (controller) {
      controller.abort();
      this.activeAbortMap.delete(conversationId);
      logger.warn("api.stream.abort-request", { conversationId });
    }
  }

  private pushMessage(conversationId: string, message: Message) {
    if (!this.messagesByConversation[conversationId]) {
      this.messagesByConversation[conversationId] = [];
    }
    const exists = this.messagesByConversation[conversationId].some((m) => m.id === message.id);
    if (!exists) {
      this.messagesByConversation[conversationId].push(message);
    }
  }
}
