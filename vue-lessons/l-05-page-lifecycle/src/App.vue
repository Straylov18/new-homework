<script setup lang="ts">
import { onMounted, ref } from 'vue'

const isLabel = ref<boolean>(false);

function showLabel() {
  // сделать isLabel true и через 5 секунд вернуть обратно
  isLabel.value = true
  setTimeout(() => {
    isLabel.value = false
  }, 3000)
}

onMounted(() => {
  showLabel()
  console.log(isLabel.value)  // вывести в консоль браузера значение isLabel
})
</script>

<template>
  <v-app>
    <v-label class="red-label" v-if="isLabel">Приложение загрузилось</v-label>
    <v-label class="red-label" v-if="isLabel">(сообщение уйдет через 3 секунды)</v-label>
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
