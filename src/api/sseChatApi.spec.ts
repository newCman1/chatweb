import { describe, expect, it, vi } from "vitest";
import type { Message } from "@/types/chat";
import { SseChatApi } from "./sseChatApi";

function textStream(text: string): ReadableStream<Uint8Array> {
  return new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(text));
      controller.close();
    }
  });
}

describe("SseChatApi", () => {
  it("parses json sse stream chunks", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      body: textStream(
        'event: chunk\ndata: {"delta":"hello "}\n\n' +
          'event: chunk\ndata: {"delta":"world"}\n\n' +
          'event: done\ndata: {"done":true}\n\n'
      )
    });
    vi.stubGlobal("fetch", fetchMock);

    const api = new SseChatApi({
      baseUrl: "http://127.0.0.1:8000/api",
      streamFormat: "json"
    });
    const messages: Message[] = [
      {
        id: "u1",
        conversationId: "c1",
        role: "user",
        content: "hello",
        status: "done",
        createdAt: new Date().toISOString()
      }
    ];

    const out: string[] = [];
    for await (const chunk of api.streamReply({ conversationId: "c1", messages })) {
      if (chunk.delta) out.push(chunk.delta);
    }
    expect(out.join("")).toBe("hello world");
  });
});
