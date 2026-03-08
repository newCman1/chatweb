import type { IChatApi } from "./chatApi";
import { MockChatApi } from "./mockChatApi";

export let chatApi: IChatApi = new MockChatApi();

export function setChatApi(api: IChatApi) {
  chatApi = api;
}
