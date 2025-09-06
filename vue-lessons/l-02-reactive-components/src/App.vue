<script setup lang="ts">
import {ref} from "vue"

const isShowing = ref<boolean>(false)

function handleClick() {
  isShowing.value = !isShowing.value
}
</script>

<template>
  <v-app>
    <v-container max-width="600">
      <v-row>
        {{ isShowing }}
        <v-btn class="v-col-12" @click="handleClick">
          Отобразить остальные элементы
        </v-btn>
        <v-col>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
