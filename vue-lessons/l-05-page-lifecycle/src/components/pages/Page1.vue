<script setup lang="ts">
import router from '@/router/index'
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
  <v-container max-width="600">
    <v-label class="blue-label" v-if="isLabel">Страница 1 загрузилось</v-label>
    <v-label class="blue-label" v-if="isLabel">(сообщение уйдет через 5 секунд)</v-label>
    <v-label>Страница 1</v-label>
    <v-btn class="v-col-12" @click="router.push('/')">
      Вернуться на главную
    </v-btn>
  </v-container>
</template>

<style scoped>
.blue-label {
  color: blue;
  font-size: 2em;
}
</style>