import type { Conversation, Message, StreamChunk } from "@/types/chat";

export interface StreamReplyInput {
  conversationId: string;
  messages: Message[];
  signal?: AbortSignal;
}

export interface IChatApi {
  listConversations(): Promise<Conversation[]>;
  createConversation(): Promise<Conversation>;
  streamReply(input: StreamReplyInput): AsyncGenerator<StreamChunk>;
  abortStream(conversationId: string): void;
}
