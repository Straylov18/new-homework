<script setup lang="ts">
import {ref} from "vue"
import ItemCard from "@/components/ItemCard.vue"

const items = ref<Object[]>([
  {
    title: 'карточка 1',
    model: 42,
  },
  {
    title: 'Товар 69',
    model: 69,
  }
])
</script>

<template>
  <v-app>
    <v-container max-width="800">
      <div class="ma-3">
        <v-row class="ma-3">
          <h1>
            Товары
          </h1>
        </v-row>
        <v-row>
          <item-card
              v-for="i in items"
              :title="i.title"
              v-model="i.model"
          />
        </v-row>
        <v-row v-for="(item, index) in items">
          {{ "Модель " + index + " элемента списка равна " + item.model }}
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
