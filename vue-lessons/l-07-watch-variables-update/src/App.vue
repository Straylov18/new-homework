<script setup lang="ts">
import { ref, watch } from 'vue'

const isLabel = ref<boolean>(false);
const inputText = ref<string>('');

function showLabel() {
  // сделать isLabel true и через 5 секунд вернуть обратно
  isLabel.value = true
  setTimeout(() => {
    isLabel.value = false
  }, 1000)
}

watch(inputText, () => {
  showLabel();
})
</script>

<template>
  <v-app>
    <v-container max-width="800">
      <v-label class="red-label" v-if="isLabel">Обновился текст</v-label>
      <v-label class="red-label" v-if="isLabel">(сообщение уйдет через секунду)</v-label>
      <v-label>При вводе текста отработает событие</v-label>
      <v-textarea v-model="inputText"></v-textarea>
    </v-container>
  </v-app>
</template>

<style scoped>
.red-label {
  color: red;
  font-size: 2em;
}
</style>
