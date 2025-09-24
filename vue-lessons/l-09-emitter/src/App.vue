<script setup lang="ts">
import {ref} from "vue"
import ProductCard from "@/components/ProductCard.vue"

const products = ref<Object[]>([
  {
    title: 'Товар 1',
    price: 42,
  },
  {
    title: 'Товар 69',
    price: 69,
  },
  {
    title: 'Лабубу',
    price: 70,
  },
  {
    title: 'Подушка',
    price: 42,
  }
])

function increaseProductPrice(position) {
  products.value[position].price += 1;
}
function decreaseProductPrice(position) {
  products.value[position].price -= 1;
}

function deleteProduct(position) {
  products.value.splice(position, 1);
}

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
          <product-card
              v-for="(p, index) in products"
              :title="p.title"
              :price="p.price"
              :index="index"
              v-on:deleteProduct="deleteProduct"
              v-on:increaseProductPrice="increaseProductPrice"
              v-on:decreaseProductPrice="decreaseProductPrice"
          />
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
