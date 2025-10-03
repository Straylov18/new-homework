<script setup lang="ts">
import InputWrapper from "@/components/InputWrapper.vue"
</script>

<template>
  <v-app>
    <v-container max-width="800">
      <div class="ma-3">
        <v-row class="ma-3">
          <h1>
            Поля ввода
          </h1>
        </v-row>
        <v-row>
          <input-wrapper
              title="Текстовое поле ввода"
          >
            <v-text-field placeholder="Введите текст"></v-text-field>
          </input-wrapper>
<!--        </v-row>-->
<!--        <v-row>-->
          <input-wrapper
              title="Свитч"
          >
            <v-switch label="Не нинтендо свитч"></v-switch>
          </input-wrapper>
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
