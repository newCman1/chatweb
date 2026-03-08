import type { Conversation, Message, StreamChunk } from "@/types/chat";

export interface StreamReplyInput {
  conversationId: string;
  messages: Message[];
  enableThinking?: boolean;
  enableWebSearch?: boolean;
  apiKey?: string;
  apiBaseUrl?: string;
  apiModel?: string;
  apiReasoningModel?: string;
  signal?: AbortSignal;
}

export interface IChatApi {
  listConversations(): Promise<Conversation[]>;
  createConversation(): Promise<Conversation>;
  listMessages(conversationId: string): Promise<Message[]>;
  streamReply(input: StreamReplyInput): AsyncGenerator<StreamChunk>;
  abortStream(conversationId: string): void;
}
