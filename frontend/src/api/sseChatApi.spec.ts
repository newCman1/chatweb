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
    for await (const chunk of api.streamReply({ conversationId: "c1", messages, enableThinking: true })) {
      if (chunk.delta) out.push(chunk.delta);
    }
    expect(out.join("")).toBe("hello world");
    const body = JSON.parse(fetchMock.mock.calls[0][1].body as string) as { enableThinking?: boolean };
    expect(body.enableThinking).toBe(true);
  });

  it("parses thinking events from sse stream", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      body: textStream(
        'event: thinking\ndata: {"delta":"analyzing "}\n\n' +
          'event: chunk\ndata: {"delta":"answer"}\n\n' +
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

    const thinking: string[] = [];
    const answer: string[] = [];
    for await (const chunk of api.streamReply({ conversationId: "c1", messages })) {
      if (chunk.thinkingDelta) thinking.push(chunk.thinkingDelta);
      if (chunk.delta) answer.push(chunk.delta);
    }
    expect(thinking.join("")).toBe("analyzing ");
    expect(answer.join("")).toBe("answer");
  });

  it("retries initial request on transient failure", async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new Error("network"))
      .mockResolvedValueOnce({
        ok: true,
        body: textStream('event: done\ndata: {"done":true}\n\n')
      });
    vi.stubGlobal("fetch", fetchMock);

    const api = new SseChatApi({
      baseUrl: "http://127.0.0.1:8000/api",
      streamFormat: "json",
      retryTimes: 1
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

    const chunks: string[] = [];
    for await (const item of api.streamReply({ conversationId: "c1", messages })) {
      if (item.delta) chunks.push(item.delta);
    }
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(chunks).toHaveLength(0);
  });

  it("throws stream error when server sends error event", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      body: textStream('event: error\ndata: {"code":"AI_PROVIDER_ERROR","message":"provider failed"}\n\n')
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

    await expect(async () => {
      for await (const _ of api.streamReply({ conversationId: "c1", messages })) {
      }
    }).rejects.toThrow("AI_PROVIDER_ERROR: provider failed");
  });
});
