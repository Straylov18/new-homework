<script setup lang="ts">
import {ref} from "vue"
const greetingMessage = ref<string>(import.meta.env.VITE_APP_GREETING_MESSAGE)
</script>

<template>
  <h1>{{ greetingMessage }}</h1>
</template>
