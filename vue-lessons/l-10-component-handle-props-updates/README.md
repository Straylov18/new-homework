# Обновление props компонентов при помощи v-model

В случае если из компонента нужно передавать 
события только об изменении свойств, 
то в props можно использовать специальное свойство v-model.

## Шаблон приложения

Для начала напишем компонент, который будет принимать props на вход, 
но не сможет изменить это значение.

Напишем компонент **components/ItemCard.vue** 
и попробуем обновить в нем входящее значения model 
при клике на кнопки:
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
          @click="model -= 1"
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
Однако здесь обновление свойств не будет передаваться наружу, 
и соответственно обновления этих свойств извне не будут работать.

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
              :model="i.model"
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

Чтобы обновление значений корректно работало, 
необходимо использовать свойство **v-model** 
при передаче значений в props компонента снаружи.
Оно автоматически будет ассоциироваться со свойством **modelValue** внутри компонента.

Тогда при использовании компонента значения будут прокидываться в v-model:
```vue
<item-card
    v-for="i in items"
    :title="i.title"
    v-model="i.model"
/>
```
А при описании компонента он будет получать на вход modelValue 
(он снаружи будет ассоциироваться с v-model).
Однако чтобы при использовании компонентов свойства v-model 
мы могли его обновить из компонента, 
необходимо добавить вызов эммитреа при обновлении поля внутри компонента.
Это можно сделать, обернув modelValue в вычисляемое значение computed.
К computed значениям можно обращаться, как к обычным переменным или константам, 
однако их значения обрабатываются в момент вызова computed значений.

Тогда обернем modelValue (получается из props) 
в localValue (computed значение), чтобы при изменении localValue 
вызывать внешнее событие на обновление modelValue 
(снаружи просто обновится v-model).
```vue
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
```
Тогда теперь везде внутри компонента 
можно использовать localValue значение вместо modelValue, например:
```vue
<v-label>{{ 'Модель: ' + localValue }}</v-label>
```

Теперь при обновлении localValue,
компонент будет вызывать обновление у v-model свойства, 
которое пришло в props.

Подробнее про v-model можно посмотреть здесь:
https://vueframework.com/docs/v3/ru/ru/guide/component-custom-events.html#валидация-сгенерированных-событии.
