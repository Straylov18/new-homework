# Обработка событий из внешних компонентов при помощи emitter привязок

При разработке компонентов web приложений очень часто в компоненте приходится вызывать какие-то внешние события, 
описанные снаружи компонента.

Для реализации этого процесса во Vue есть возможность в определенный момент в коде компонента 
сообщать о необходимости вызвать событие.
В наружном же компоненте можно описать ожидание вызова каких-либо событий и исполнять определенный код, 
если такой вызов произошел.

## Базовое приложение с карточками товаров

Пусть у нас существует компонент карточки продуктов **components/ProductCard.vue**:
```vue
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
      <v-btn class="v-col-4 delete-card-btn">Удалить</v-btn>
      <v-btn class="v-col-4 card-btn">Стонкс</v-btn>
      <v-btn class="v-col-4 card-btn">Не стонкс</v-btn>
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
```

Который мы используем в основном приложении **App.vue**:
```vue
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
          />
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>

<style scoped>
</style>
```

### Иконки

Добавим кнопкам иконки, чтобы те были компактнее. 
Для этого установим дополнительные библиотеки для работы с mdi (material design icons) иконками:
```shell
npm i material-design-icons-iconfont @mdi/font
```

Чтобы данную библиотеку можно было использовать, импортируем ее в **main.ts**, 
тогда он будет выглядеть следующим образом:
```tsimport { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { createVuetify } from 'vuetify'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'


const vuetify = createVuetify({})
createApp(App).use(vuetify).mount('#app')
```

Теперь добавим иконки кнопкам в **components/ProductCard.vue**:
```vue
    <v-row class="card-row">
      <v-btn
          class="delete-card-btn"
          flat
          icon="mdi-trash-can-outline"
      ></v-btn>
      <v-spacer/>
      <v-btn
          class="card-btn"
          flat
          icon="mdi-numeric-positive-1"
      ></v-btn>
      <v-spacer/>
      <v-btn
          class="card-btn"
          flat
          icon="mdi-numeric-negative-1"
      ></v-btn>
  </v-row>
```

Все существующие mdi иконки и их названия можно посмотреть здесь:
https://pictogrammers.com/library/mdi/icon.

## Использование emitter во Vue

Теперь добавим обработку нажатия на кнопки в компонентах.

Поскольку компонент карточки продукта **components/ProductCard.vue** 
не может манипулировать списком продуктов, описанном в **App.vue**, 
необходимо описывать работу со списком продуктов в **App.vue**.

Напишем в **App.vue** функции, отвечающие за изменение цены и удаление соответствующего продукта 
(по его позиции в списке):
```ts
function increaseProductPriceFunc(position) {
  products.value[position].price += 1;
}

function decreaseProductPriceFunc(position) {
  products.value[position].price -= 1;
}

function deleteProductFunc(position) {
  products.value.splice(position, 1);
}
```

Однако эти методы необходимо вызывать из самого компонента.
Для этого как раз и нужен emit метод.

Запросим обработку события при нажатии на кнопки в компоненте:
```vue
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
```

В **App.vue** привяжем вызов событий из компонентов к запуску соответствующих функций, описанных в **App.vue**:
```vue
<product-card
    v-for="(p, index) in products"
    :title="p.title"
    :price="p.price"
    :index="index"
    v-on:deleteProduct="deleteProductFunc"
    v-on:increaseProductPrice="increaseProductPrice"
    v-on:decreaseProductPrice="decreaseProductPrice"
/>
```

Теперь при нажатии на кнопки компонентов (**components/ProductCard.vue**), 
будут меняться данные там, где эти компоненты описывались (**App.vue**).
