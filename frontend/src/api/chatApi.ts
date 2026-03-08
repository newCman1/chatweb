import type { Conversation, Message, StreamChunk } from "@/types/chat";

export interface StreamReplyInput {
  conversationId: string;
  messages: Message[];
  enableThinking?: boolean;
  signal?: AbortSignal;
}

export interface IChatApi {
  listConversations(): Promise<Conversation[]>;
  createConversation(): Promise<Conversation>;
  listMessages(conversationId: string): Promise<Message[]>;
  streamReply(input: StreamReplyInput): AsyncGenerator<StreamChunk>;
  abortStream(conversationId: string): void;
}
