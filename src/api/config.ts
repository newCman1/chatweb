export const apiConfig = {
  mode: (import.meta.env.VITE_CHAT_API_MODE ?? "mock") as "mock" | "sse",
  baseUrl: import.meta.env.VITE_CHAT_API_BASE_URL ?? "http://127.0.0.1:8000/api",
  streamFormat: (import.meta.env.VITE_CHAT_STREAM_FORMAT ?? "json") as "json" | "binary",
  requestTimeoutMs: Number(import.meta.env.VITE_CHAT_API_TIMEOUT_MS ?? 10000),
  retryTimes: Number(import.meta.env.VITE_CHAT_API_RETRY_TIMES ?? 1)
};
