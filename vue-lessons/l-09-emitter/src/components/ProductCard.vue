<script setup lang="ts">
const props = defineProps({
  title: {
    type: String,
    default: null,
  },
  price: {
    type: Number,
    default: 0,
  },
  index: {
    type: Number,
    default: 0,
  },
})
</script>

<template>
  <v-container class="v-col-4 main-product-container ma-3">
    <v-row class="header-row">
      <h2>
        {{ title }}
      </h2>
    </v-row>
    <v-row class="card-row">
      <v-label>{{ 'Цена: ' + price }}</v-label>
    </v-row>
    <v-row class="card-row">
      <v-btn class="v-col-4 card-btn" @click="$emit('deleteProduct', index)">Удалить</v-btn>
      <v-btn class="v-col-4 card-btn" @click="$emit('increaseProductPrice', index)">Стонкс</v-btn>
      <v-btn class="v-col-4 card-btn" @click="$emit('decreaseProductPrice', index)">Не стонкс</v-btn>
    </v-row>
  </v-container>
</template>

<style scoped>
.main-product-container {
  border-radius: 10px;
  background-color: #888888;
}
.main-product-container:hover {
  background-color: #808080;
}

.header-row {
  padding-left: 12px;
  padding-top: 4px;
  margin-bottom: 12px;
}

.card-row {
  margin: 4px 0 4px 0px;
}

.card-btn {
  background-color: #666666;
}
</style>