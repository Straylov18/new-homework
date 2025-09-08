<script setup lang="ts">
import router from '@/router/index'
</script>

<template>
  <v-container max-width="600">
    <v-label>Страница 1</v-label>
    <v-btn class="v-col-12" @click="router.push('/')">
      Вернуться на главную
    </v-btn>
  </v-container>
</template>

<style scoped>

</style>