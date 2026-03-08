import type {
  Conversation,
  Message,
  StreamChunk,
  SupervisorRun,
  UploadAttachment
} from "@/types/chat";

export interface StreamReplyInput {
  conversationId: string;
  messages: Message[];
  enableThinking?: boolean;
  enableWebSearch?: boolean;
  attachments?: UploadAttachment[];
  apiKey?: string;
  apiBaseUrl?: string;
  apiModel?: string;
  apiReasoningModel?: string;
  signal?: AbortSignal;
}

export interface SupervisorRunInput {
  conversationId: string;
  objective: string;
  plan?: string;
  maxTasks?: number;
  maxRetries?: number;
}

export interface IChatApi {
  listConversations(): Promise<Conversation[]>;
  createConversation(): Promise<Conversation>;
  listMessages(conversationId: string): Promise<Message[]>;
  streamReply(input: StreamReplyInput): AsyncGenerator<StreamChunk>;
  abortStream(conversationId: string): void;
  runSupervisor(input: SupervisorRunInput): Promise<SupervisorRun>;
  startSupervisor(input: SupervisorRunInput): Promise<SupervisorRun>;
  getSupervisor(runId: string): Promise<SupervisorRun>;
  abortSupervisor(runId: string): Promise<SupervisorRun>;
}
