# Слоты под компоненты внутри других компонентов

Порой необходимо сделать одинаковую обертку из компонентов 
под разные компоненты. 
Для этого можно использовать слоты, в компоненте-обертке.

## Тег <slot></slot>

Напишем компонент-обертку, 
внутри которого на месте оборачиваемого компонента будет тег slot:
```vue
<script setup lang="ts">
const props = defineProps({
  title: {
    type: String,
    default: null,
  }
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
      <slot></slot>
    </v-row>
  </v-container>
</template>

<style scoped>
.main-product-container {
  border-radius: 10px;
  background-color: #bababa;
}

.header-row {
  padding-left: 12px;
  padding-top: 4px;
  margin-bottom: 12px;
}

.card-row {
  margin: 4px 0 4px 0px;
}
</style>
```

Тогда в основном приложении можно будет вызвать этот компонент-обертку и в нем описать, 
что должно быть на месте тега slot:
```vue
<script setup lang="ts">
import InputWrapper from "@/components/InputWrapper.vue"
</script>

<template>
  <v-app>
    <v-container max-width="800">
      <div class="ma-3">
        <v-row class="ma-3">
          <h1>
            Поля ввода
          </h1>
        </v-row>
        <v-row>
          <input-wrapper
              title="Текстовое поле ввода"
          >
            <v-text-field placeholder="Введите текст"></v-text-field>
          </input-wrapper>
          <input-wrapper
              title="Свитч"
          >
            <v-switch label="Не нинтендо свитч"></v-switch>
          </input-wrapper>
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
```

## Несколько слотов в одном компоненте (именованные слоты)

В одном компоненте может быть также несколько слотов, 
которые можно вызывать поименно.

Например, добавим именованный слот в **InputWrapper.vue**:
```vue
    <v-row class="card-row">
      <slot name="cardFooter"></slot>
    </v-row>
```

Тогда в **App.vue** при использовании элементов 
можно описать второй слот в отдельном месте:
```vue

<v-row>
  <input-wrapper
      title="Текстовое поле ввода"
  >
    <v-text-field placeholder="Введите текст"></v-text-field>

    <template v-slot:cardFooter>
      <!-- content for the cardFooter slot -->
      {{ 'Футер для карточки ввода текста' }}
    </template>
  </input-wrapper>
  <input-wrapper
      title="Свитч"
  >
    <template v-slot:cardFooter>
      <!-- content for the cardFooter slot -->
      {{ 'Футер для карточки со свичом' }}
    </template>
    <v-switch label="Не нинтендо свитч"></v-switch>
  </input-wrapper>
</v-row>
```
Как видно, от последовательности описания слотов, результат не меняется.

## Использование props для слотов

[//]: # (TODO)

Подробнее о слотах можно почитать тут:
https://vuejs.org/guide/components/slots.html.
