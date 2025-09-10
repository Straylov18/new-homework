# Переход между страницами с использованием Vue router

Раньше web приложения подгружали каждую страницу отдельно с сервера 
при каждом изменении пути в строке браузера.
Сейчас принято делать так называемые **single page applications**, 
которые один раз выкачивают всю информацию о конфигурации web приложении в браузер, 
и потом при изменении пути уже делают обращения только к бэкенду 
без дополнительной загрузки html, css, js контента.
Таким образом приложение меньше подвисает при переходе между страницами.

Изменение страницы же при переходе между адресами в таких случаях 
осуществляется во фреймворках через отдельный модуль роутинга.

## Vue router

Чтобы оперировать с переходами между страницами в рамках приложения, 
установим модель vue-router:
```shell
npm i vue-router
```
Как обычно, модуль нужно добавить в импорты в **main.ts**:
```vue
import { createApp } from 'vue'
import "./style.css"
import App from "./App.vue"
import router from "./router"
import { createVuetify } from 'vuetify'
import 'vuetify/styles'


const vuetify = createVuetify({})
createApp(App)
    .use(router)
    .use(vuetify)
    .mount('#app')
```

Создадим файл **router/index.ts**, в котором опишем пути страниц приложения:
```ts
import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '@/components/pages/MainPage.vue'
import Page1 from '@/components/pages/Page1.vue'
import Page2 from '@/components/pages/Page2.vue'

const routes = [
  {
    name: "Main",
    path: "/",
    component: MainPage,
  },
  {
    name: "Page1",
    path: "/page1",
    component: Page1
  },
  {
    name: "Page2",
    path: "/page2",
    component: Page2
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
```
Тут говорится, что страницы будут описаны в файлах 
**/components/pages/MainPage.vue**, **/components/pages/Page1.vue**, **/components/pages/Page2.vue**.
Их опишем чуть позже.

Чтобы отобразить страницы приложения, 
добавим в разделе **template** в **App.vue** тэг <vMain>, 
содержащий внутри себя тэг <routerView/>:
```vue
<template>
  <v-app>
    <v-label>Элементы чердака (хэдера) можно добавлять тут</v-label>
    <vMain>
      <routerView/>
    </vMain>
    <v-label>Элементы подвала (футера) можно добавлять тут</v-label>
  </v-app>
</template>
```
Тут на место тега <routerView/> будут подставляться страницы роутера.
Остальные элементы с **App.vue** будут общими для всех страниц.

[//]: # (TODO описание для:)
[//]: # (**/components/pages/MainPage.vue**, **/components/pages/Page1.vue**, **/components/pages/Page2.vue**)

Подробнее об использовании роутинга во vue приложении можно почитать тут:
https://vuejs.org/guide/scaling-up/routing.html.
