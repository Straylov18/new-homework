<script setup lang="ts">
import {ref} from "vue";
const clickedTimes = ref(0)
</script>

<template>
  <v-container class="v-col-4 main-product-container ma-3">
    <v-btn @click="clickedTimes ++" >
      Жмякнуть!
    </v-btn>
    <slot :clickedTimes="clickedTimes"></slot>
  </v-container>
</template>

<style scoped>
.main-product-container {
  border-radius: 10px;
  background-color: #bababa;
}
</style>