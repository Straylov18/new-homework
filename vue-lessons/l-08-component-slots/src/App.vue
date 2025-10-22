<script setup lang="ts">
import InputWrapper from "@/components/InputWrapper.vue"
import Clicker from "@/components/Clicker.vue"
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
        <v-row>
          <h1>
            Кастомные кликеры:
          </h1>
        </v-row>
        <v-row>
          <clicker>
            <template #default="{ clicks }">
              <p>
                {{ "кликов: " + clicks }}
              </p>
            </template>
          </clicker>
          <clicker>
            <template #default="{ clicks }">
              <h2 class="clicker-output pa-1 my-2">
                {{ clicks }}
              </h2>
            </template>
          </clicker>
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>

<style scoped>
.clicker-output {
  outline: #535bf2 solid 2px;
  border-radius: 5px;
  background-color: rgba(83, 91, 242, 0.26);
}
.clicker-output:hover {
  filter: drop-shadow(0 0 0.5em #646cff);
}
</style>
