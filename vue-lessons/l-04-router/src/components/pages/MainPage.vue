<script setup lang="ts">
import router from '@/router/index'

</script>

<template>
  <v-container max-width="600">
    <v-label>Главная страница</v-label>
    <v-btn class="v-col-12" @click="router.push('/page1')">
      Страница 1
    </v-btn>
    <v-btn class="v-col-12" @click="router.push('/page2')">
      Страница 2
    </v-btn>
  </v-container>
</template>

<style scoped>

</style>