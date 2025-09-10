<script setup lang="ts">
import { onMounted, ref } from 'vue'

const isLabel = ref<boolean>(false);

function showLabel() {
  isLabel.value = true
  setTimeout(() => {
    isLabel.value = false
  }, 5000)
}

onMounted(() => {
  showLabel()
  console.log(isLabel.value)
})
</script>

<template>
  <v-app>
    <v-label class="red-label" v-if="isLabel">Приложение загрузилось</v-label>
    <v-label class="red-label" v-if="isLabel">(сообщение уйдет через 5 секунд)</v-label>
    <vMain>
      <routerView />
    </vMain>
  </v-app>
</template>

<style scoped>
.red-label {
  color: red;
  font-size: 2em;
}
</style>
