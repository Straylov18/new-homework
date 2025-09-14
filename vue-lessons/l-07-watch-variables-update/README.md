# Запуск функций в момент обновления переменных

Порой необходимо знать, 
когда та или иная переменная обновилась, 
чтобы выполнить в этот момент какое-то действие.

Для этого во vue есть функция **watch**, 
которая позволяет привязать выполнение кода к событию изменения конкретной переменной. 

Допустим, в приложении есть текстовое поле, 
значение текста которого привязанное к переменной "inputText":
```vue
<script setup lang="ts">
  import { ref } from 'vue'
  
  const inputText = ref<string>('');
</script>

<template>
  <v-app>
    <v-container max-width="800">
      <v-textarea v-model="inputText"></v-textarea>
    </v-container>
  </v-app>
</template>
```

Добавим вызов функции **watch**, который привяжет событие "showLabel" к переменной "inputText":
```vue
<script setup lang="ts">
import { ref, watch } from 'vue'

const isLabel = ref<boolean>(false);
const inputText = ref<string>('');

function showLabel() {
  // сделать isLabel true и через 5 секунд вернуть обратно
  isLabel.value = true
  setTimeout(() => {
    isLabel.value = false
  }, 1000)
}

watch(inputText, () => {
  showLabel();
})
</script>
```
При вызове **watch** здесь:
- в первом параметре обозначается переменная, обновление которой будет проверяться
- во втором параметре указывается лямбда-функция, которая будет исполняться при обновлении переменной

Чтобы проверить, что функция отработала, тут вешается таймер на переключение булиновкой переменной.
Привяжем к этой переменной отображение сообщения.
Тогда описание шаблона будет выглядеть:
```vue
<template>
  <v-app>
    <v-container max-width="800">
      <v-label class="red-label" v-if="isLabel">Обновился текст</v-label>
      <v-label class="red-label" v-if="isLabel">(сообщение уйдет через секунду)</v-label>
      <v-label>При вводе текста отработает событие</v-label>
      <v-textarea v-model="inputText"></v-textarea>
    </v-container>
  </v-app>
</template>

<style scoped>
  .red-label {
    color: red;
    font-size: 2em;
  }
</style>
```

Также в описываемой лямбда-функции можно получать 
старое и новое значение переменной для обработки своего события.
Также функция **watch** может проверять изменения в сложных вложенных структурах, 
для этого 3-м параметром ем можно передать значение "{ deep: true }".
Подробнее об этих и многих других полезных настройках функции **watch** можно почитать тут:
https://vuejs.org/guide/essentials/watchers.html.
