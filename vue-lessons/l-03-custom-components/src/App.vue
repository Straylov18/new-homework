<script setup lang="ts">
import {ref} from "vue"
import ProductCard from "./components/ProductCard.vue";

const products = ref<Object[]>([
  {
    title: 'Товар 1',
    price: 42,
    params: [
      'надежный',
      'дешевый',
    ],
  },
  {
    title: 'Товар 2',
    price: 4200,
    params: [
      'надежный',
      'дорогой',
    ],
  },
  {
    title: 'Товар 69',
    price: 69,
    params: [
      'ну тут понятно',
      'еще параметр',
    ],
  },
])
</script>

<template>
  <v-app>
    <v-container max-width="900">
      <div class="ma-3">
        <v-row class="ma-3">
          <h1>
            Товары
          </h1>
        </v-row>
        <v-row>
          <product-card
              v-for="p in products"
              :title="p.title"
              :price="p.price"
              :parameters-list="p.params"
          />
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
