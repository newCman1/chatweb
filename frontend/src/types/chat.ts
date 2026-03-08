export type MessageRole = "user" | "assistant" | "system";

export type MessageStatus = "streaming" | "done" | "stopped" | "error";

export interface Message {
  id: string;
  conversationId: string;
  role: MessageRole;
  content: string;
  thinking?: string;
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
  thinkingDelta?: string;
  done?: boolean;
}

export interface UploadAttachment {
  name: string;
  mimeType: string;
  content: string;
  size: number;
}

export interface ApiError {
  code: string;
  message: string;
}

export type SupervisorRunStatus = "running" | "completed" | "failed" | "aborted";

export type SupervisorTaskStatus = "running" | "completed" | "failed" | "aborted";

export interface SupervisorTask {
  index: number;
  title: string;
  workerOutput: string;
  reviewVerdict: string;
  reviewFeedback: string;
  status: SupervisorTaskStatus;
  retries: number;
}

export interface SupervisorRun {
  id: string;
  conversationId: string;
  objective: string;
  planText: string;
  primaryName: string;
  workerName: string;
  status: SupervisorRunStatus;
  summary: string;
  createdAt: string;
  tasks: SupervisorTask[];
}
