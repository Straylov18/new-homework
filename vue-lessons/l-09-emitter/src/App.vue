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

function increaseProductPriceFunc(position) {
  products.value[position].price += 1;
}

function decreaseProductPriceFunc(position) {
  products.value[position].price -= 1;
}

function deleteProductFunc(position) {
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
              v-on:deleteProduct="deleteProductFunc"
              v-on:increaseProductPrice="increaseProductPriceFunc"
              v-on:decreaseProductPrice="decreaseProductPriceFunc"
          />
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
