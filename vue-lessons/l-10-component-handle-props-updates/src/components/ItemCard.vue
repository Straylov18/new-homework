<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps({
  title: {
    type: String,
    default: null,
  },
  modelValue: {
    type: Number,
    default: 0,
  }
})
const emit = defineEmits(['update:modelValue', 'update:'])
const localValue = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

function increaseModel() {
  localValue.value += 1
}

function decreaseModel() {
  localValue.value -= 1
}
</script>

<template>
  <v-container class="v-col-4 main-product-container ma-3">
    <v-row class="header-row">
      <h2>
        {{ title }}
      </h2>
    </v-row>
    <v-row class="card-row">
      <v-label>{{ 'Модель: ' + localValue }}</v-label>
    </v-row>
    <v-row class="card-row">
      <v-btn
          class="card-btn"
          flat
          icon="mdi-numeric-positive-1"
          @click="increaseModel()"
      ></v-btn>
      <v-btn
          class="card-btn"
          flat
          icon="mdi-numeric-negative-1"
          @click="decreaseModel()"
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

.card-btn {
  background-color: #0000;
}
</style>