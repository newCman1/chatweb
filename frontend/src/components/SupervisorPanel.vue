<script setup lang="ts">
import { computed, ref } from "vue";
import type { SupervisorRunStatus } from "@/types/chat";

const props = withDefaults(
  defineProps<{
    disabled?: boolean;
    status?: SupervisorRunStatus | null;
  }>(),
  {
    disabled: false,
    status: null
  }
);

const emit = defineEmits<{
  start: [payload: { objective: string; plan?: string; maxTasks: number; maxRetries: number }];
  abort: [];
}>();

const objective = ref("");
const plan = ref("");
const maxTasks = ref(4);
const maxRetries = ref(1);

const running = computed(() => props.status === "running");
const canStart = computed(() => !props.disabled && !running.value && objective.value.trim().length > 0);
const statusText = computed(() => {
  if (!props.status) return "Idle";
  if (props.status === "running") return "Running";
  if (props.status === "completed") return "Completed";
  if (props.status === "aborted") return "Aborted";
  return "Failed";
});

function onStart() {
  if (!canStart.value) return;
  emit("start", {
    objective: objective.value.trim(),
    plan: plan.value.trim() || undefined,
    maxTasks: Math.max(1, Math.min(8, maxTasks.value)),
    maxRetries: Math.max(0, Math.min(3, maxRetries.value))
  });
}
</script>

<template>
  <section class="supervisor-panel">
    <div class="supervisor-head">
      <h3>Supervisor Mode</h3>
      <span class="status-chip" :class="status ?? 'idle'">{{ statusText }}</span>
    </div>
    <div class="supervisor-form">
      <label>
        Objective
        <input v-model="objective" placeholder="Tell Primary AI your goal..." :disabled="disabled || running" />
      </label>
      <label>
        Plan (Optional)
        <textarea
          v-model="plan"
          rows="2"
          placeholder="1. Task one&#10;2. Task two"
          :disabled="disabled || running"
        />
      </label>
      <div class="supervisor-inline">
        <label>
          Max Tasks
          <input v-model.number="maxTasks" type="number" min="1" max="8" :disabled="disabled || running" />
        </label>
        <label>
          Max Retries
          <input v-model.number="maxRetries" type="number" min="0" max="3" :disabled="disabled || running" />
        </label>
      </div>
      <div class="supervisor-actions">
        <button type="button" class="run-btn" :disabled="!canStart" @click="onStart">Start Supervisor</button>
        <button type="button" class="abort-btn" :disabled="!running" @click="$emit('abort')">Stop Supervisor</button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.supervisor-panel {
  border-bottom: 1px solid var(--border);
  background: #f7fbff;
  padding: 10px 20px;
}

.supervisor-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.supervisor-head h3 {
  margin: 0;
  font-size: 13px;
  color: var(--text-main);
}

.status-chip {
  font-size: 11px;
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 2px 8px;
  color: var(--text-secondary);
  background: #fff;
}

.status-chip.running {
  border-color: #93c5fd;
  color: #1d4ed8;
}

.status-chip.completed {
  border-color: #86efac;
  color: #15803d;
}

.status-chip.failed {
  border-color: #fca5a5;
  color: #dc2626;
}

.status-chip.aborted {
  border-color: #fcd34d;
  color: #a16207;
}

.supervisor-form {
  display: grid;
  gap: 8px;
}

label {
  display: grid;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

input,
textarea {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 9px;
  font-size: 12px;
  font-family: var(--font-main);
  color: var(--text-main);
  background: #fff;
}

textarea {
  resize: vertical;
}

.supervisor-inline {
  display: grid;
  grid-template-columns: 140px 140px;
  gap: 10px;
}

.supervisor-actions {
  display: inline-flex;
  gap: 8px;
}

.run-btn,
.abort-btn {
  border-radius: 8px;
  border: 1px solid var(--border);
  background: #fff;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 600;
}

.run-btn:disabled,
.abort-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.run-btn:not(:disabled):hover {
  border-color: #93c5fd;
  color: #1d4ed8;
}

.abort-btn:not(:disabled):hover {
  border-color: #fca5a5;
  color: #dc2626;
}
</style>
