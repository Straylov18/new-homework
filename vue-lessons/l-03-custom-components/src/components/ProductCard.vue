<script setup lang="ts">
const props = defineProps({
  title: {
    type: String,
    default: null,
  },
  parametersList: {
    type: Array<string>,
    default: [],
  },
  price: {
    type: Number,
    default: 0,
  },
  discount: {
    type: Number,
    default: 0,
  },
})
</script>

<template>
  <v-container class="main-product-container">
    <v-row class="header-row">
      <h2>
        {{ title }}
      </h2>
    </v-row>
    <v-row class="card-row">
      <v-col class="ma-0 pa-0">
        <v-row class="parameter-row">
          <v-label>{{ 'Параметры:' }}</v-label>
        </v-row>
        <v-row class="parameter-row" v-for="i in parametersList.length">
          <v-label>{{ '- ' + parametersList[i-1] }}</v-label>
        </v-row>
      </v-col>
    </v-row>
    <v-row class="card-row">
      <v-label v-if="!discount">{{ 'Цена: ' + price }}</v-label>
      <v-label v-if="discount">
        {{ `Цена: ${price-discount}` }}
      </v-label>
      <v-label v-if="discount" class="discount-price ml-1">{{ price }}</v-label>
    </v-row>
    <v-row class="card-row">
      <v-btn class="v-col-12 add-btn">Добавить в корзину</v-btn>
    </v-row>
  </v-container>
</template>

<style scoped>
.main-product-container {
  width: 256px;
  height: 256px;
  border-radius: 10px;
  background-color: #888888;
}
.main-product-container:hover {
  background-color: #808080;
}

.header-row {
  padding-left: 8px;
  margin-bottom: 4px;
}

.card-row {
  margin: 4px 0 4px 0px;
}

.parameter-row {
  margin: 4px;
}

.discount-price {
  text-decoration: line-through;
}

.add-btn {
  background-color: #666666;
}
</style>