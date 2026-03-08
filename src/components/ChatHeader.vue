<script setup lang="ts">
defineProps<{
  title: string;
}>();
</script>

<template>
  <header class="chat-header">
    <h1>{{ title }}</h1>
    <p>Desktop Prototype</p>
  </header>
</template>
