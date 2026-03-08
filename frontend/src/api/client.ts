import type { IChatApi } from "./chatApi";
import { apiConfig } from "./config";
import { MockChatApi } from "./mockChatApi";
import { SseChatApi } from "./sseChatApi";

function createDefaultApi(): IChatApi {
  if (apiConfig.mode === "sse") {
    return new SseChatApi({
      baseUrl: apiConfig.baseUrl,
      streamFormat: apiConfig.streamFormat,
      requestTimeoutMs: apiConfig.requestTimeoutMs,
      retryTimes: apiConfig.retryTimes
    });
  }
  return new MockChatApi();
}

export let chatApi: IChatApi = createDefaultApi();

export function setChatApi(api: IChatApi) {
  chatApi = api;
}
