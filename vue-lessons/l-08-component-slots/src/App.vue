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

            <template v-slot:cardFooter>
              <!-- content for the cardFooter slot -->
              {{ 'Футер для карточки ввода текста' }}
            </template>
          </input-wrapper>
          <input-wrapper
              title="Свитч"
          >
            <template v-slot:cardFooter>
              <!-- content for the cardFooter slot -->
              {{ 'Футер для карточки со свичом' }}
            </template>
            <v-switch label="Не нинтендо свитч"></v-switch>
          </input-wrapper>
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
