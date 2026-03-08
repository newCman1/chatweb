<script setup lang="ts">
import type { SupervisorRun, SupervisorRunStatus } from "@/types/chat";
import { computed } from "vue";

const props = defineProps<{
  currentRun: SupervisorRun | null;
  status: SupervisorRunStatus | null;
  recentRuns: SupervisorRun[];
}>();

const statusLabel = computed(() => {
  if (!props.status) return "Idle";
  if (props.status === "running") return "Running";
  if (props.status === "completed") return "Completed";
  if (props.status === "aborted") return "Aborted";
  return "Failed";
});
</script>

<template>
  <section class="supervisor-board">
    <div class="board-header">
      <h3>Supervisor Board</h3>
      <span class="status-pill" :class="status ?? 'idle'">{{ statusLabel }}</span>
    </div>

    <div v-if="currentRun" class="current-run">
      <p class="run-meta">Run ID: {{ currentRun.id }}</p>
      <p class="run-meta">Objective: {{ currentRun.objective }}</p>
      <p class="run-summary" v-if="currentRun.summary">{{ currentRun.summary }}</p>
      <div class="task-table-wrap">
        <table class="task-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Task</th>
              <th>Status</th>
              <th>Retries</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in currentRun.tasks" :key="`${currentRun.id}-${task.index}`">
              <td>{{ task.index }}</td>
              <td>{{ task.title }}</td>
              <td>{{ task.status }}</td>
              <td>{{ task.retries }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <p v-else class="empty-tip">No supervisor run selected.</p>

    <div class="history">
      <h4>Recent Runs</h4>
      <ul v-if="recentRuns.length > 0">
        <li v-for="run in recentRuns.slice(0, 6)" :key="run.id">
          <span class="run-id">{{ run.id.slice(0, 8) }}</span>
          <span class="run-status" :class="run.status">{{ run.status }}</span>
          <span class="run-objective">{{ run.objective }}</span>
        </li>
      </ul>
      <p v-else class="empty-tip">No run history.</p>
    </div>
  </section>
</template>

<style scoped>
.supervisor-board {
  border-bottom: 1px solid var(--border);
  padding: 10px 20px;
  background: #f9fbff;
  display: grid;
  gap: 10px;
}

.board-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.board-header h3 {
  margin: 0;
  font-size: 13px;
}

.status-pill {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 11px;
  color: var(--text-secondary);
  background: #fff;
}

.status-pill.running {
  border-color: #93c5fd;
  color: #1d4ed8;
}

.status-pill.completed {
  border-color: #86efac;
  color: #15803d;
}

.status-pill.failed {
  border-color: #fca5a5;
  color: #dc2626;
}

.status-pill.aborted {
  border-color: #fcd34d;
  color: #a16207;
}

.run-meta {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.run-summary {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-main);
}

.task-table-wrap {
  overflow-x: auto;
}

.task-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-top: 6px;
}

.task-table th,
.task-table td {
  border: 1px solid var(--border-light);
  padding: 5px 6px;
  text-align: left;
}

.task-table th {
  background: #eef4ff;
  color: var(--text-secondary);
}

.history h4 {
  margin: 0 0 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.history ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 4px;
}

.history li {
  display: grid;
  grid-template-columns: 74px 72px 1fr;
  gap: 8px;
  align-items: center;
  font-size: 12px;
}

.run-id {
  font-family: var(--font-mono);
  color: var(--text-tertiary);
}

.run-status {
  border: 1px solid var(--border);
  border-radius: 999px;
  text-align: center;
  font-size: 11px;
  padding: 1px 6px;
  background: #fff;
}

.run-status.running {
  border-color: #93c5fd;
  color: #1d4ed8;
}

.run-status.completed {
  border-color: #86efac;
  color: #15803d;
}

.run-status.failed {
  border-color: #fca5a5;
  color: #dc2626;
}

.run-status.aborted {
  border-color: #fcd34d;
  color: #a16207;
}

.run-objective {
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-tip {
  margin: 0;
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
