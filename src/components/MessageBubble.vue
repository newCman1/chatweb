<script setup lang="ts">
import type { Message } from "@/types/chat";

defineProps<{
  message: Message;
}>();
</script>

<template>
  <article class="message-row" :class="message.role">
    <div class="message-bubble" :class="message.role">
      <div class="message-content">{{ message.content }}</div>
      <small v-if="message.status !== 'done'" class="status">{{ message.status }}</small>
    </div>
  </article>
</template>
