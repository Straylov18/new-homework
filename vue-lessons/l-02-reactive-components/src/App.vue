<script setup lang="ts">
import {ref} from "vue"

const inputText = ref<string>("")
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
      </v-row>
      <v-row v-if="isShowing && true">
        <v-textarea v-model="inputText"></v-textarea>
      </v-row>
      <v-row v-if="isShowing && true">
        <v-btn v-for="(char, index) in inputText">
          <v-label :style="`color: rgb(${index*10}, 0, ${index*2})`">
            {{ char }}
          </v-label>
        </v-btn>
      </v-row>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
