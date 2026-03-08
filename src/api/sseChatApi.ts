import type { Conversation, Message, StreamChunk } from "@/types/chat";
import type { IChatApi, StreamReplyInput } from "./chatApi";

interface SseChatApiOptions {
  baseUrl: string;
  streamFormat: "json" | "binary";
}

const headers = {
  "Content-Type": "application/json"
};

export class SseChatApi implements IChatApi {
  private readonly baseUrl: string;
  private readonly streamFormat: "json" | "binary";
  private readonly activeAbortMap = new Map<string, AbortController>();

  constructor(options: SseChatApiOptions) {
    this.baseUrl = options.baseUrl.replace(/\/+$/, "");
    this.streamFormat = options.streamFormat;
  }

  async listConversations(): Promise<Conversation[]> {
    const response = await fetch(`${this.baseUrl}/conversations`);
    if (!response.ok) throw new Error(`listConversations failed: ${response.status}`);
    const data = (await response.json()) as { conversations: Conversation[] };
    return data.conversations ?? [];
  }

  async createConversation(): Promise<Conversation> {
    const response = await fetch(`${this.baseUrl}/conversations`, {
      method: "POST"
    });
    if (!response.ok) throw new Error(`createConversation failed: ${response.status}`);
    const data = (await response.json()) as { conversation: Conversation };
    return data.conversation;
  }

  async *streamReply(input: StreamReplyInput): AsyncGenerator<StreamChunk> {
    const userMessage = [...input.messages].reverse().find((m) => m.role === "user");
    const content = userMessage?.content?.trim() ?? "";
    if (!content) throw new Error("No user content to stream");

    const controller = new AbortController();
    this.activeAbortMap.set(input.conversationId, controller);
    if (input.signal) {
      input.signal.addEventListener("abort", () => controller.abort(), { once: true });
    }

    try {
      const response = await fetch(`${this.baseUrl}/chat/stream`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          conversationId: input.conversationId,
          content,
          streamFormat: this.streamFormat
        }),
        signal: controller.signal
      });
      if (!response.ok || !response.body) {
        throw new Error(`streamReply failed: ${response.status}`);
      }

      if (this.streamFormat === "binary") {
        yield* this.readBinaryStream(response.body);
      } else {
        yield* this.readSseStream(response.body);
      }
    } catch (error) {
      if (error instanceof DOMException && error.name === "AbortError") {
        const abortError = new Error("Stream aborted");
        abortError.name = "AbortError";
        throw abortError;
      }
      throw error;
    } finally {
      this.activeAbortMap.delete(input.conversationId);
    }
  }

  abortStream(conversationId: string): void {
    const controller = this.activeAbortMap.get(conversationId);
    if (controller) {
      controller.abort();
      this.activeAbortMap.delete(conversationId);
      void fetch(`${this.baseUrl}/chat/abort`, {
        method: "POST",
        headers,
        body: JSON.stringify({ conversationId })
      });
    }
  }

  private async *readBinaryStream(stream: ReadableStream<Uint8Array>): AsyncGenerator<StreamChunk> {
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      if (!value) continue;
      const delta = decoder.decode(value, { stream: true });
      if (delta) yield { delta };
    }
    yield { delta: "", done: true };
  }

  private async *readSseStream(stream: ReadableStream<Uint8Array>): AsyncGenerator<StreamChunk> {
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      if (!value) continue;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";

      for (const rawEvent of events) {
        const parsed = this.parseSseEvent(rawEvent);
        if (!parsed) continue;
        if (parsed.event === "chunk") {
          try {
            const payload = JSON.parse(parsed.data) as { delta?: string };
            if (payload.delta) yield { delta: payload.delta };
          } catch {
            continue;
          }
        }
        if (parsed.event === "done") {
          yield { delta: "", done: true };
          return;
        }
      }
    }

    yield { delta: "", done: true };
  }

  private parseSseEvent(rawEvent: string): { event: string; data: string } | null {
    const lines = rawEvent.split("\n");
    let event = "message";
    let data = "";
    for (const line of lines) {
      if (line.startsWith("event:")) {
        event = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        data += line.slice(5).trim();
      }
    }
    if (!data && event !== "done") return null;
    return { event, data };
  }
}
