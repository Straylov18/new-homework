<script setup lang="ts">
import {ref} from 'vue'

const props = defineProps<{
  title: {
    type: String,
    default: null,
  },
  parametersList: {
    type: Array<string>,
    default: [],
  },
  price: {
    type: number,
    default: 0,
  },
}>()

const count = ref(0)
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
      <v-label>{{ 'Цена: ' + price }}</v-label>
    </v-row>
    <v-row class="card-row">
      <v-btn class="add-btn">Добавить</v-btn>
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

.add-btn {
  background-color: #666666;
}
</style>