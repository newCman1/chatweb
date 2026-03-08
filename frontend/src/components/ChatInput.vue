<script setup lang="ts">
import { computed, ref } from "vue";
import type { UploadAttachment } from "@/types/chat";

const props = withDefaults(
  defineProps<{
    disabled?: boolean;
    isStreaming: boolean;
    enableDeepThinking: boolean;
    enableWebSearch?: boolean;
    userApiKey?: string;
    userApiBaseUrl?: string;
    userApiModel?: string;
    userApiReasoningModel?: string;
  }>(),
  {
    disabled: false,
    enableWebSearch: false,
    userApiKey: "",
    userApiBaseUrl: "",
    userApiModel: "",
    userApiReasoningModel: ""
  }
);

const emit = defineEmits<{
  send: [payload: { content: string; attachments: UploadAttachment[] }];
  stop: [];
  "update:enableDeepThinking": [value: boolean];
  "update:enableWebSearch": [value: boolean];
  "update:userApiKey": [value: string];
  "update:userApiBaseUrl": [value: string];
  "update:userApiModel": [value: string];
  "update:userApiReasoningModel": [value: string];
}>();

const draft = ref("");
const settingsOpen = ref(false);
const revealApiKey = ref(false);
const fileInputRef = ref<HTMLInputElement | null>(null);
const selectedAttachments = ref<UploadAttachment[]>([]);
const attachmentError = ref("");

const MAX_ATTACHMENTS = 5;
const MAX_FILE_SIZE = 1_500_000;
const MAX_TEXT_LENGTH = 12_000;

const textMimePrefixes = ["text/"];
const textMimeTypes = new Set(["application/json", "application/xml", "application/yaml"]);
const textExtensions = new Set(["txt", "md", "markdown", "json", "csv", "log", "xml", "yaml", "yml"]);

const canSend = computed(
  () =>
    !props.disabled &&
    !props.isStreaming &&
    (draft.value.trim().length > 0 || selectedAttachments.value.length > 0)
);
const actionLabel = computed(() => (props.isStreaming ? "Stop" : "Send"));

function onSend() {
  const content = draft.value.trim();
  if ((!content && selectedAttachments.value.length === 0) || props.disabled || props.isStreaming) return;
  emit("send", {
    content,
    attachments: [...selectedAttachments.value]
  });
  draft.value = "";
  selectedAttachments.value = [];
  attachmentError.value = "";
}

function onPrimaryAction() {
  if (props.isStreaming) {
    emit("stop");
    return;
  }
  onSend();
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    onSend();
  }
}

function onToggleDeepThinking(event: Event) {
  const target = event.target as HTMLInputElement;
  emit("update:enableDeepThinking", target.checked);
}

function onToggleWebSearch(event: Event) {
  const target = event.target as HTMLInputElement;
  emit("update:enableWebSearch", target.checked);
}

function triggerFilePicker() {
  fileInputRef.value?.click();
}

function removeAttachment(index: number) {
  selectedAttachments.value = selectedAttachments.value.filter((_, i) => i !== index);
}

function isTextFile(file: File): boolean {
  if (textMimePrefixes.some((prefix) => file.type.startsWith(prefix))) return true;
  if (textMimeTypes.has(file.type)) return true;
  const ext = file.name.split(".").pop()?.toLowerCase() ?? "";
  return textExtensions.has(ext);
}

function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(typeof reader.result === "string" ? reader.result : "");
    reader.onerror = () => reject(new Error(`Read file failed: ${file.name}`));
    reader.readAsText(file);
  });
}

async function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const files = Array.from(input.files ?? []);
  input.value = "";
  attachmentError.value = "";
  if (!files.length) return;

  const next = [...selectedAttachments.value];
  for (const file of files) {
    if (next.length >= MAX_ATTACHMENTS) {
      attachmentError.value = `At most ${MAX_ATTACHMENTS} files can be attached.`;
      break;
    }
    if (file.size > MAX_FILE_SIZE) {
      attachmentError.value = `File too large: ${file.name} (max ${Math.floor(MAX_FILE_SIZE / 1000)}KB).`;
      continue;
    }

    try {
      if (isTextFile(file)) {
        const content = (await readFileAsText(file)).slice(0, MAX_TEXT_LENGTH);
        next.push({ name: file.name, mimeType: file.type || "text/plain", content, size: file.size });
        continue;
      }
      attachmentError.value = `Unsupported file type: ${file.name}. Use text/json/csv/md/log/xml/yaml.`;
    } catch {
      attachmentError.value = `Cannot load file: ${file.name}`;
    }
  }
  selectedAttachments.value = next;
}
</script>

<template>
  <footer class="chat-input-wrap">
    <div class="chat-input-container">
      <textarea
        v-model="draft"
        class="chat-input"
        placeholder="Type your message..."
        :disabled="disabled"
        rows="3"
        @keydown="onKeydown"
      />
      <div class="chat-input-toolbar">
        <div class="left-tools">
          <button class="settings-btn" type="button" @click="triggerFilePicker">Attach</button>
          <input
            ref="fileInputRef"
            class="file-input"
            type="file"
            accept=".txt,.md,.markdown,.json,.csv,.log,.xml,.yaml,.yml,text/*,application/json,application/xml,application/yaml"
            multiple
            @change="onFileChange"
          />
          <label class="thinking-toggle">
            <input
              data-testid="deep-thinking-toggle"
              type="checkbox"
              :checked="enableDeepThinking"
              @change="onToggleDeepThinking"
            />
            <span class="toggle-text">Deep thinking</span>
          </label>
          <label class="thinking-toggle">
            <input
              data-testid="web-search-toggle"
              type="checkbox"
              :checked="enableWebSearch"
              @change="onToggleWebSearch"
            />
            <span class="toggle-text">Web search</span>
          </label>
          <button class="settings-btn" type="button" @click="settingsOpen = !settingsOpen">
            {{ settingsOpen ? "Hide API" : "API Settings" }}
          </button>
        </div>

        <div class="input-actions">
          <span class="input-hint"><kbd>Enter</kbd> send, <kbd>Shift</kbd>+<kbd>Enter</kbd> newline</span>
          <button
            class="primary-btn"
            :class="{ stop: isStreaming }"
            :disabled="isStreaming ? false : !canSend"
            @click="onPrimaryAction"
          >
            {{ actionLabel }}
          </button>
        </div>
      </div>

      <div v-if="selectedAttachments.length > 0" class="attachment-list">
        <span v-for="(item, index) in selectedAttachments" :key="`${item.name}-${index}`" class="attachment-chip">
          {{ item.name }}
          <button type="button" @click="removeAttachment(index)">x</button>
        </span>
      </div>
      <p v-if="attachmentError" class="attachment-error">{{ attachmentError }}</p>

      <div v-if="settingsOpen" class="api-settings">
        <div class="api-row">
          <label for="chatweb-api-key">API Key</label>
          <div class="api-key-input">
            <input
              id="chatweb-api-key"
              data-testid="api-key-input"
              :type="revealApiKey ? 'text' : 'password'"
              :value="userApiKey"
              placeholder="sk-..."
              @input="emit('update:userApiKey', ($event.target as HTMLInputElement).value)"
            />
            <button type="button" class="secondary-btn" @click="revealApiKey = !revealApiKey">
              {{ revealApiKey ? "Hide" : "Show" }}
            </button>
          </div>
        </div>
        <div class="api-row">
          <label for="chatweb-api-base-url">Base URL</label>
          <input
            id="chatweb-api-base-url"
            :value="userApiBaseUrl"
            placeholder="https://api.deepseek.com/v1"
            @input="emit('update:userApiBaseUrl', ($event.target as HTMLInputElement).value)"
          />
        </div>
        <div class="api-grid">
          <div class="api-row">
            <label for="chatweb-api-model">Model</label>
            <input
              id="chatweb-api-model"
              :value="userApiModel"
              placeholder="deepseek-chat"
              @input="emit('update:userApiModel', ($event.target as HTMLInputElement).value)"
            />
          </div>
          <div class="api-row">
            <label for="chatweb-api-reasoning-model">Reasoning Model</label>
            <input
              id="chatweb-api-reasoning-model"
              :value="userApiReasoningModel"
              placeholder="deepseek-reasoner"
              @input="emit('update:userApiReasoningModel', ($event.target as HTMLInputElement).value)"
            />
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.chat-input-wrap {
  border-top: 1px solid var(--border);
  padding: 16px 20px 18px;
  background: var(--bg-panel);
}

.chat-input-container {
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 14px;
  transition: all var(--transition-fast);
}

.chat-input-container:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--brand-soft);
}

.chat-input {
  width: 100%;
  min-height: 52px;
  max-height: 180px;
  padding: 12px 14px;
  border: none;
  border-radius: 14px 14px 0 0;
  background: transparent;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-main);
  resize: none;
  outline: none;
  font-family: var(--font-main);
}

.chat-input::placeholder {
  color: var(--text-tertiary);
}

.chat-input-toolbar {
  border-top: 1px solid var(--border-light);
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.left-tools {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.thinking-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  user-select: none;
}

.thinking-toggle input {
  margin: 0;
}

.settings-btn,
.secondary-btn {
  border: 1px solid var(--border);
  background: #fff;
  color: var(--text-secondary);
  border-radius: 8px;
  font-size: 12px;
  padding: 6px 8px;
  cursor: pointer;
}

.file-input {
  display: none;
}

.settings-btn:hover,
.secondary-btn:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
}

.input-actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.input-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  white-space: nowrap;
}

.input-hint kbd {
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 5px;
  font-family: var(--font-mono);
  font-size: 11px;
}

.primary-btn {
  border: none;
  border-radius: 10px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  color: #fff;
  background: var(--brand);
  transition: all var(--transition-fast);
  min-width: 72px;
}

.primary-btn:hover:not(:disabled) {
  background: var(--brand-strong);
}

.primary-btn.stop {
  background: var(--danger);
}

.primary-btn.stop:hover {
  background: #dc2626;
}

.primary-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.api-settings {
  border-top: 1px solid var(--border-light);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #fafcff;
}

.api-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.api-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.api-row label {
  font-size: 12px;
  color: var(--text-secondary);
}

.api-row input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 13px;
  font-family: var(--font-main);
}

.api-key-input {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 12px 0;
}

.attachment-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--border);
  background: var(--bg-soft);
  color: var(--text-secondary);
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 12px;
}

.attachment-chip button {
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  font-size: 12px;
  padding: 0;
}

.attachment-error {
  margin: 6px 12px 0;
  color: var(--danger);
  font-size: 12px;
}
</style>
