<script setup lang="ts">
import router from '@/router/index'
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
  <v-container max-width="600">
    <v-label class="green-label" v-if="isLabel">Главная страница загрузилась</v-label>
    <v-label class="green-label" v-if="isLabel">(сообщение уйдет через 3 секунды)</v-label>
    <v-label>Главная страница</v-label>
    <v-btn class="v-col-12" @click="router.push('/page1')">
      Страница 1
    </v-btn>
  </v-container>
</template>

<style scoped>
.green-label {
  color: green;
  font-size: 2em;
}
</style>