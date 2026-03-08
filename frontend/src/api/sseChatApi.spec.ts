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
    const body = JSON.parse(fetchMock.mock.calls[0][1].body as string) as {
      enableThinking?: boolean;
      enableWebSearch?: boolean;
    };
    expect(body.enableThinking).toBe(true);
    expect(body.enableWebSearch).toBe(false);
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

  it("sends runtime api options in stream payload", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      body: textStream('event: done\ndata: {"done":true}\n\n')
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

    for await (const _ of api.streamReply({
      conversationId: "c1",
      messages,
      enableWebSearch: true,
      apiKey: "sk-123",
      apiBaseUrl: "https://api.deepseek.com/v1",
      apiModel: "deepseek-chat",
      apiReasoningModel: "deepseek-reasoner",
      attachments: [
        {
          name: "notes.txt",
          mimeType: "text/plain",
          content: "attachment content",
          size: 18
        }
      ]
    })) {
    }
    const body = JSON.parse(fetchMock.mock.calls[0][1].body as string) as Record<string, unknown>;
    expect(body.enableWebSearch).toBe(true);
    expect(body.apiKey).toBe("sk-123");
    expect(body.apiBaseUrl).toBe("https://api.deepseek.com/v1");
    expect(body.apiModel).toBe("deepseek-chat");
    expect(body.apiReasoningModel).toBe("deepseek-reasoner");
    expect(Array.isArray(body.attachments)).toBe(true);
  });

  it("calls supervisor start/get/abort endpoints", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          run: {
            id: "r1",
            conversationId: "c1",
            objective: "obj",
            planText: "",
            primaryName: "Primary AI",
            workerName: "Worker AI",
            status: "running",
            summary: "",
            createdAt: new Date().toISOString(),
            tasks: []
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          run: {
            id: "r1",
            conversationId: "c1",
            objective: "obj",
            planText: "",
            primaryName: "Primary AI",
            workerName: "Worker AI",
            status: "completed",
            summary: "done",
            createdAt: new Date().toISOString(),
            tasks: []
          }
        })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          run: {
            id: "r1",
            conversationId: "c1",
            objective: "obj",
            planText: "",
            primaryName: "Primary AI",
            workerName: "Worker AI",
            status: "aborted",
            summary: "aborted",
            createdAt: new Date().toISOString(),
            tasks: []
          }
        })
      });
    vi.stubGlobal("fetch", fetchMock);

    const api = new SseChatApi({
      baseUrl: "http://127.0.0.1:8000/api",
      streamFormat: "json"
    });

    const started = await api.startSupervisor({ conversationId: "c1", objective: "obj" });
    expect(started.status).toBe("running");
    const current = await api.getSupervisor("r1");
    expect(current.status).toBe("completed");
    const aborted = await api.abortSupervisor("r1");
    expect(aborted.status).toBe("aborted");

    expect((fetchMock.mock.calls[0][0] as string).endsWith("/supervisor/run/start")).toBe(true);
    expect((fetchMock.mock.calls[1][0] as string).endsWith("/supervisor/run/r1")).toBe(true);
    expect((fetchMock.mock.calls[2][0] as string).endsWith("/supervisor/run/r1/abort")).toBe(true);
  });
});
