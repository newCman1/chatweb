import { defineStore } from "pinia";
import { chatApi } from "@/api/client";
import { useConversationStore } from "./conversation";
import type { Message, SupervisorRun, SupervisorRunStatus, UploadAttachment } from "@/types/chat";
import { logger } from "@/utils/logger";

interface ChatState {
  isStreaming: boolean;
  activeConversationId: string | null;
  activeAssistantMessageId: string | null;
  activeAbortController: AbortController | null;
  errorText: string | null;
  enableDeepThinking: boolean;
  enableWebSearch: boolean;
  userApiKey: string;
  userApiBaseUrl: string;
  userApiModel: string;
  userApiReasoningModel: string;
  thinkingExpandedByMessageId: Record<string, boolean>;
  supervisorRunId: string | null;
  supervisorStatus: SupervisorRunStatus | null;
  supervisorActiveConversationId: string | null;
  supervisorSeenEventKeys: Record<string, boolean>;
}

const uid = () => crypto.randomUUID();
const now = () => new Date().toISOString();
const DEEP_THINKING_PREF_KEY = "chatweb.enableDeepThinking";
const WEB_SEARCH_PREF_KEY = "chatweb.enableWebSearch";
const USER_API_KEY = "chatweb.userApiKey";
const USER_API_BASE_URL = "chatweb.userApiBaseUrl";
const USER_API_MODEL = "chatweb.userApiModel";
const USER_API_REASONING_MODEL = "chatweb.userApiReasoningModel";
const SUPERVISOR_POLL_MS = 1000;

function loadDeepThinkingPreference(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(DEEP_THINKING_PREF_KEY) === "1";
}

function loadWebSearchPreference(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(WEB_SEARCH_PREF_KEY) === "1";
}

function loadTextPreference(key: string, fallback = ""): string {
  if (typeof window === "undefined") return fallback;
  return window.localStorage.getItem(key) ?? fallback;
}

function saveTextPreference(key: string, value: string): void {
  if (typeof window === "undefined") return;
  const trimmed = value.trim();
  if (!trimmed) {
    window.localStorage.removeItem(key);
    return;
  }
  window.localStorage.setItem(key, trimmed);
}

export const useChatStore = defineStore("chat", {
  state: (): ChatState => ({
    isStreaming: false,
    activeConversationId: null,
    activeAssistantMessageId: null,
    activeAbortController: null,
    errorText: null,
    enableDeepThinking: loadDeepThinkingPreference(),
    enableWebSearch: loadWebSearchPreference(),
    userApiKey: loadTextPreference(USER_API_KEY),
    userApiBaseUrl: loadTextPreference(USER_API_BASE_URL),
    userApiModel: loadTextPreference(USER_API_MODEL),
    userApiReasoningModel: loadTextPreference(USER_API_REASONING_MODEL),
    thinkingExpandedByMessageId: {},
    supervisorRunId: null,
    supervisorStatus: null,
    supervisorActiveConversationId: null,
    supervisorSeenEventKeys: {}
  }),
  actions: {
    async send(payload: { content: string; attachments?: UploadAttachment[] }) {
      const trimmed = payload.content.trim();
      const attachments = payload.attachments ?? [];
      if ((!trimmed && attachments.length === 0) || this.isStreaming) return;

      const conversationStore = useConversationStore();
      if (!conversationStore.currentConversationId) {
        await conversationStore.createConversation();
      }

      const conversationId = conversationStore.currentConversationId;
      if (!conversationId) return;

      this.errorText = null;
      logger.info("chat.send", {
        conversationId,
        contentLength: trimmed.length,
        attachmentsCount: attachments.length,
        enableWebSearch: this.enableWebSearch,
        apiKeyProvided: Boolean(this.userApiKey.trim())
      });
      const withAttachmentHints =
        attachments.length > 0
          ? `${trimmed}${trimmed ? "\n\n" : ""}[Attached files]\n${attachments.map((item) => `- ${item.name}`).join("\n")}`
          : trimmed;
      const userMessage: Message = {
        id: uid(),
        conversationId,
        role: "user",
        content: withAttachmentHints,
        status: "done",
        createdAt: now()
      };
      conversationStore.addMessage(userMessage);

      const assistantMessageId = uid();
      const assistantMessage: Message = {
        id: assistantMessageId,
        conversationId,
        role: "assistant",
        content: "",
        thinking: "",
        status: "streaming",
        createdAt: now()
      };
      conversationStore.addMessage(assistantMessage);

      this.isStreaming = true;
      this.activeConversationId = conversationId;
      this.activeAssistantMessageId = assistantMessageId;
      this.activeAbortController = new AbortController();
      logger.info("chat.stream.start", { conversationId, assistantMessageId });

      try {
        const stream = chatApi.streamReply({
          conversationId,
          messages: conversationStore.messagesByConversation[conversationId],
          enableThinking: this.enableDeepThinking,
          enableWebSearch: this.enableWebSearch,
          apiKey: this.userApiKey || undefined,
          apiBaseUrl: this.userApiBaseUrl || undefined,
          apiModel: this.userApiModel || undefined,
          apiReasoningModel: this.userApiReasoningModel || undefined,
          attachments: attachments.length ? attachments : undefined,
          signal: this.activeAbortController.signal
        });
        for await (const chunk of stream) {
          if (chunk.delta) {
            const current = conversationStore.messagesByConversation[conversationId].find(
              (m) => m.id === assistantMessageId
            );
            const next = `${current?.content ?? ""}${chunk.delta}`;
            conversationStore.patchMessage(conversationId, assistantMessageId, {
              content: next
            });
          }
          if (chunk.thinkingDelta) {
            const current = conversationStore.messagesByConversation[conversationId].find(
              (m) => m.id === assistantMessageId
            );
            const nextThinking = `${current?.thinking ?? ""}${chunk.thinkingDelta}`;
            conversationStore.patchMessage(conversationId, assistantMessageId, {
              thinking: nextThinking
            });
          }
          if (chunk.done) {
            conversationStore.patchMessage(conversationId, assistantMessageId, {
              status: "done"
            });
            logger.info("chat.stream.done", { conversationId, assistantMessageId });
          }
        }
      } catch (err) {
        const isAbort = err instanceof Error && err.name === "AbortError";
        conversationStore.patchMessage(conversationId, assistantMessageId, {
          status: isAbort ? "stopped" : "error"
        });
        if (!isAbort) {
          this.errorText = "Generation failed, please retry.";
          logger.error("chat.stream.error", {
            conversationId,
            assistantMessageId,
            enableWebSearch: this.enableWebSearch,
            apiKeyProvided: Boolean(this.userApiKey.trim()),
            error: err instanceof Error ? err.message : "unknown"
          });
        } else {
          logger.warn("chat.stream.stopped", { conversationId, assistantMessageId });
        }
      } finally {
        this.isStreaming = false;
        this.activeConversationId = null;
        this.activeAssistantMessageId = null;
        this.activeAbortController = null;
      }
    },
    stop() {
      if (!this.isStreaming || !this.activeConversationId) return;
      logger.warn("chat.stop.requested", { conversationId: this.activeConversationId });
      this.activeAbortController?.abort();
      chatApi.abortStream(this.activeConversationId);
    },
    async startSupervisor(payload: {
      objective: string;
      plan?: string;
      maxTasks?: number;
      maxRetries?: number;
    }) {
      const objective = payload.objective.trim();
      if (!objective) {
        this.errorText = "Supervisor objective is required.";
        return;
      }
      const conversationStore = useConversationStore();
      if (!conversationStore.currentConversationId) {
        await conversationStore.createConversation();
      }
      const conversationId = conversationStore.currentConversationId;
      if (!conversationId) return;

      this.errorText = null;
      logger.info("supervisor.start.request", {
        conversationId,
        objectiveLength: objective.length
      });

      try {
        const run = await chatApi.startSupervisor({
          conversationId,
          objective,
          plan: payload.plan?.trim() || undefined,
          maxTasks: payload.maxTasks ?? 4,
          maxRetries: payload.maxRetries ?? 1
        });
        this.supervisorRunId = run.id;
        this.supervisorStatus = run.status;
        this.supervisorActiveConversationId = conversationId;
        this.ingestSupervisorRun(run, conversationId);
        if (run.status === "running") {
          void this.pollSupervisor(run.id, conversationId);
        }
      } catch (err) {
        this.errorText = "Supervisor start failed.";
        logger.error("supervisor.start.error", {
          conversationId,
          error: err instanceof Error ? err.message : "unknown"
        });
      }
    },
    async abortSupervisor() {
      const runId = this.supervisorRunId;
      if (!runId) return;
      try {
        const run = await chatApi.abortSupervisor(runId);
        const conversationId = this.supervisorActiveConversationId ?? run.conversationId;
        this.ingestSupervisorRun(run, conversationId);
        this.supervisorStatus = run.status;
        if (run.status !== "running") {
          this.supervisorRunId = null;
        }
      } catch (err) {
        this.errorText = "Supervisor abort failed.";
        logger.error("supervisor.abort.error", { error: err instanceof Error ? err.message : "unknown" });
      }
    },
    setEnableDeepThinking(enable: boolean) {
      this.enableDeepThinking = enable;
      if (typeof window !== "undefined") {
        window.localStorage.setItem(DEEP_THINKING_PREF_KEY, enable ? "1" : "0");
      }
    },
    setEnableWebSearch(enable: boolean) {
      this.enableWebSearch = enable;
      if (typeof window !== "undefined") {
        window.localStorage.setItem(WEB_SEARCH_PREF_KEY, enable ? "1" : "0");
      }
    },
    setUserApiKey(value: string) {
      this.userApiKey = value;
      saveTextPreference(USER_API_KEY, value);
    },
    setUserApiBaseUrl(value: string) {
      this.userApiBaseUrl = value;
      saveTextPreference(USER_API_BASE_URL, value);
    },
    setUserApiModel(value: string) {
      this.userApiModel = value;
      saveTextPreference(USER_API_MODEL, value);
    },
    setUserApiReasoningModel(value: string) {
      this.userApiReasoningModel = value;
      saveTextPreference(USER_API_REASONING_MODEL, value);
    },
    isThinkingExpanded(messageId: string): boolean {
      return this.thinkingExpandedByMessageId[messageId] === true;
    },
    toggleThinkingExpanded(messageId: string) {
      this.thinkingExpandedByMessageId[messageId] = !this.isThinkingExpanded(messageId);
    },
    async pollSupervisor(runId: string, conversationId: string) {
      while (this.supervisorRunId === runId) {
        await new Promise<void>((resolve) => {
          setTimeout(resolve, SUPERVISOR_POLL_MS);
        });
        try {
          const run = await chatApi.getSupervisor(runId);
          this.ingestSupervisorRun(run, conversationId);
          this.supervisorStatus = run.status;
          if (run.status !== "running") {
            this.supervisorRunId = null;
            return;
          }
        } catch (err) {
          this.errorText = "Supervisor polling failed.";
          this.supervisorRunId = null;
          this.supervisorStatus = "failed";
          logger.error("supervisor.poll.error", {
            runId,
            error: err instanceof Error ? err.message : "unknown"
          });
          return;
        }
      }
    },
    ingestSupervisorRun(run: SupervisorRun, conversationId: string) {
      const conversationStore = useConversationStore();

      for (const task of run.tasks) {
        if (task.status === "running") continue;
        const workerKey = `run:${run.id}:task:${task.index}:worker`;
        if (!this.supervisorSeenEventKeys[workerKey] && task.workerOutput.trim()) {
          conversationStore.addMessage({
            id: uid(),
            conversationId,
            role: "assistant",
            content: `[${run.workerName}] Task ${task.index}: ${task.title}\n${task.workerOutput}`,
            status: "done",
            createdAt: now()
          });
          this.supervisorSeenEventKeys[workerKey] = true;
        }

        const reviewKey = `run:${run.id}:task:${task.index}:review`;
        if (!this.supervisorSeenEventKeys[reviewKey]) {
          conversationStore.addMessage({
            id: uid(),
            conversationId,
            role: "assistant",
            content:
              `[${run.primaryName}] Review Task ${task.index}: ${task.reviewVerdict}\n` +
              `${task.reviewFeedback || "No feedback."}`,
            status: "done",
            createdAt: now()
          });
          this.supervisorSeenEventKeys[reviewKey] = true;
        }
      }

      const summaryKey = `run:${run.id}:summary`;
      if (!this.supervisorSeenEventKeys[summaryKey] && run.status !== "running" && run.summary.trim()) {
        conversationStore.addMessage({
          id: uid(),
          conversationId,
          role: "assistant",
          content: `[${run.primaryName}] Supervisor summary (${run.status})\n${run.summary}`,
          status: run.status === "failed" ? "error" : "done",
          createdAt: now()
        });
        this.supervisorSeenEventKeys[summaryKey] = true;
      }
    }
  }
});
