export type MessageRole = "user" | "assistant" | "system";

export type MessageStatus = "streaming" | "done" | "stopped" | "error";

export interface Message {
  id: string;
  conversationId: string;
  role: MessageRole;
  content: string;
  status: MessageStatus;
  createdAt: string;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
}

export interface StreamChunk {
  delta: string;
  done?: boolean;
}

export interface ApiError {
  code: string;
  message: string;
}
