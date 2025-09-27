# Обработка событий из внешних компонентов при помощи emitter привязок

[//]: # (TODO)

При разработке компонентов web приложений очень часто в компоненте приходится вызывать какие-то внешние события, 
описанные снаружи компонента.

Для реализации этого процесса во Vue есть возможность в определенный момент в коде компонента 
сообщать о необходимости вызвать событие.
В наружном же компоненте можно описать ожидание вызова каких-либо событий и исполнять определенный код, 
если такой вызов произошел.

## Базовое приложение с карточками

[//]: # (TODO)

Без рабочих обновлений **components/ItemCard.vue**:
```vue
<script setup lang="ts">
  const props = defineProps({
    title: {
      type: String,
      default: null,
    },
    model: {
      type: Number,
      default: 0,
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
      <v-label>{{ 'Модель: ' + model }}</v-label>
    </v-row>
    <v-row class="card-row">
      <v-btn
          class="card-btn"
          flat
          icon="mdi-numeric-positive-1"
          @click="model += 1"
      ></v-btn>
      <v-btn
          class="card-btn"
          flat
          icon="mdi-numeric-negative-1"
          @click="model --"
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
```

Который мы используем в основном приложении **App.vue**:
```vue
<script setup lang="ts">
  import {ref} from "vue"
  import ItemCard from "@/components/ItemCard.vue"

  const items = ref<Object[]>([
    {
      title: 'карточка 1',
      model: 42,
    },
    {
      title: 'Товар 69',
      model: 69,
    }
  ])
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
          <item-card
              v-for="i in items"
              :title="i.title"
              :modelValue="i.model"
          />
        </v-row>
        <v-row v-for="(item, index) in items">
          {{ "Модель " + index + " элемента списка равна " + item.model }}
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
```

## v-model

[//]: # (TODO)

Подробнее про v-model можно посмотреть здесь:
https://vueframework.com/docs/v3/ru/ru/guide/component-custom-events.html#валидация-сгенерированных-событии.
