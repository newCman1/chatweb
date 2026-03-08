import type { Conversation, StreamChunk } from "@/types/chat";
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
    "这是一个前端 mock 流式回复。后端接入后，只需要替换 API 适配器，不需要改动页面组件。";
  const tips =
    "建议下一步加入真实 SSE 接口、会话持久化和错误码映射。";
  return `你刚刚说的是：${userText}\n\n${base}\n${tips}`;
}

export class MockChatApi implements IChatApi {
  private conversations: Conversation[] = [];
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
      title: "新会话",
      createdAt: now,
      updatedAt: now
    };
    this.conversations.unshift(conversation);
    logger.info("api.createConversation", { conversationId: conversation.id });
    return conversation;
  }

  async *streamReply(input: StreamReplyInput): AsyncGenerator<StreamChunk> {
    const external = input.signal;
    const internal = new AbortController();
    this.activeAbortMap.set(input.conversationId, internal);
    logger.info("api.stream.start", { conversationId: input.conversationId });
    const userMessage = [...input.messages].reverse().find((m) => m.role === "user");
    const fullText = buildAssistantReply(userMessage?.content ?? "");
    const chunks = splitToChunks(fullText);

    try {
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
}
