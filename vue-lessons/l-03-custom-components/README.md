# Создание своих компонентов

При разработке web приложений очень часто приходится переиспользовать 
большие блоки кода в разных местах страницы или вообще на разных страницах.

Чтобы не переписывать огромные куски логики каждый раз 
принято оборачивать наборы элементов в компоненты.
Потом можно делать большие компоненты, состоящие из маленьких итд.

Использование компонентов также упрощает внесение правок в проект, 
так как в таком случае не требуется вспоминать все места где встречался определенный блок кода.

## Создание компонента на примере карточки товара

Допустим в проекте есть html и css описание карточки товара 
(сильно упрощенный вариант, описание карточки товара на реальных проектах еще больше):
```vue
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
```

Можем вынести это описание в отдельный компонент, 
который опишем в отдельном файле **components/ProductCard.vue**.
В зависимости от структуры на разных проектах фалы компонентов складывают в разные папки.
В нашем случае для упрощения все компоненты будут лежать в папке **components**.

Поскольку переменные это файла будут обособлены от переменных страниц, 
на которых будет располагаться этот файл, 
необходимо прокинуть переменные страницы в компонент.
Это можно сделать во vue с помощью так называемых **props**.

Зададим для нашего компонента **props** в файле **components/ProductCard.vue**:
```vue
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
```
Как видишь, в props можно указывать тип входящего параметра, 
его значение по умолчанию и прочие характеристики входящих переменных.

Теперь можно импортировать получившийся компонент на нужную страницу 
и вставить его в шаблон в нужных местах.

Например, добавим в **App.vue** два раздела с набором карточек продукта:
```vue
<script setup lang="ts">
  import {ref} from "vue"
  import ProductCard from "./components/ProductCard.vue"

  const products = ref<Object[]>([
    {
      title: 'Товар 1',
      price: 42,
      params: [
        'надежный',
        'дешевый',
      ],
    },
    {
      title: 'Товар 2',
      price: 4200,
      params: [
        'надежный',
        'дорогой',
      ],
    },
    {
      title: 'Товар 69',
      price: 69,
      params: [
        'ну тут понятно',
        'еще параметр',
      ],
    },
  ])

  const productsWithDiscount = ref<Object[]>([
    {
      title: 'Подушка',
      price: 42,
      discount: 3,
      params: [
        'большая',
        'перьевая',
      ],
    },
    {
      title: 'Лабубу',
      price: 70,
      discount: 11,
      params: [
        'хайпово',
        'все берут',
      ],
    },
  ])

</script>

<template>
  <v-app>
    <v-container max-width="900">
      <div class="ma-3">
        <v-row class="ma-3">
          <h1>
            Товары
          </h1>
        </v-row>
        <v-row>
          <product-card
              v-for="p in products"
              :title="p.title"
              :price="p.price"
              :parameters-list="p.params"
          />
        </v-row>
        <v-row class="ma-3">
          <h1>
            Товары по скидке
          </h1>
        </v-row>
        <v-row>
          <product-card
              v-for="p in productsWithDiscount"
              :title="p.title"
              :price="p.price"
              :discount="p.discount"
              :parameters-list="p.params"
          />
        </v-row>
      </div>
    </v-container>
  </v-app>
</template>
```

Если бы мы не использовали компонент, 
код был бы почти в два раза длиннее.
В данном случае же нам достаточно импортировать компонент строчкой:
```vue
import ProductCard from "./components/ProductCard.vue"
```
И в нужном месте вставить его тегом "<product-card ... />" 
(название файла компонента переписанное в kebab-case формате).
Можно вставлять компонент и тегом "<ProductCard ... />", 
но лучше придерживаться всеобщей конвенции об именовании тегов!

В принципе описание раздела продуктов тоже повторяется, 
так что его тоже можно вынести в отдельный компонент, 
чтобы описание главной страницы стало еще проще 
в случае появления дополнительных категорий товаров.
В рамках данного урока это делаться не будет.
