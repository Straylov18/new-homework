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
      <v-btn
          class="delete-card-btn"
          flat
          icon="mdi-trash-can-outline"
          @click="$emit('deleteProduct', index)"
      ></v-btn>
      <v-spacer/>
      <v-btn
          class="card-btn"
          flat
          icon="mdi-numeric-positive-1"
          @click="$emit('increaseProductPrice', index)"
      ></v-btn>
      <v-spacer/>
      <v-btn
          class="card-btn"
          flat
          icon="mdi-numeric-negative-1"
          @click="$emit('decreaseProductPrice', index)"
      ></v-btn>
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

.delete-card-btn {
  color: #a14646;
  background-color: #0000;
}

.card-btn {
  background-color: #0000;
}
</style>