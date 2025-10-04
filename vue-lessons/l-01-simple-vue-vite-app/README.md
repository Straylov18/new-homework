# Создание простых приложений через (Vue 3 + TypeScript + Vite)

Для работы с фронтенд приложениями необходимо для начала установить npm 
(см. https://github.com/TheYeniseiTrireme/homework-materials/blob/main/run-apps-locally/README.md).

Далее для генерации пакетов базовой структуры приложения можно использовать команду:
```shell
npm create vite@latest
```
Она спросит тебя имя проекта, а также какой фреймворк и язык ты хочешь использовать в нем.
В данном курсе мы будем работать с фреймворком Vue, а в качестве языка использовать TypeScript.
Подробнее о сборке с использованием vite можно прочитать тут https://vite.dev/guide/.

Созданное приложение уже можно запустить, установив перед этим все необходимое зависимости:
```shell
npm i  # установить все зависимости, описанные в package.json
npm run dev  # запустить приложение в режиме разработки
```

После успешного запуска приложение скажет адрес по которому оно доступно в браузере, например:
```shell
Local:   http://localhost:5173/
```

Когда вызывается команда "npm run dev", npm смотрит инструкцию по ее вызову в файле **package.json** в секции **scripts**.
По умолчанию эта секция выглядит следующим образом:
```json
"scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview"
},
```

Чтобы изменить порт, на котором приложение будет запускаться, можно изменить команду запуска приложения в **package.json**:
```json
"scripts": {
    "dev": "vite --port 3000 --host localhost",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview"
},
```

Также в дальнейшем мы будем использовать библиотеку vuetify 
для использования шаблонов компонентов.
Установим ее с помощью npm:
```shell
npm i vuetify
```

Также можно установить пакеты для упрощения отладки
(их лучше устанавливать в devDependencies, чтобы они не использовались при итоговой сборке):
```shell
npm i vite-plugin-html vite-plugin-vue-devtools vite-plugin-vuetify --save-dev
```
Благодаря пакету **vite-plugin-html** vite быстрее собирает html шаблоны в проекте.

Благодаря пакету **vite-plugin-vue-devtools** 
ты сможешь использовать отладочное меню снизу странице в браузере 
(там появится иконка с буквой V). 
Оно дает тебе возможность исследовать элементы в том виде, 
в котором они прописаны в .vue файлах (в отличие от обычного отладочного окна браузера на F12), 
смотреть значения всех переменных страницы и много других полезных вещей.
Подробнее об этом плагине можно почитать тут: https://devtools.vuejs.org/guide/vite-plugin.

Благодаря пакету **vite-plugin-vuetify** ты сможешь удобнее работать с библиотекой vuetify при использовании vite сборщика.
Например, с этим плагином не нужно импортировать стили и компоненты vuetify в каждом файле, чтобы их использовать.


## Использование компонентов из vuetify

Для использования элементов vuetify необходимо добавить его как плагин в **vite.config.ts**.
Также добавим туда vueDevTools.
Тогда **vite.config.ts** будет выглядеть:
```ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from "vite-plugin-vuetify"
import vueDevTools from "vite-plugin-vue-devtools"

export default defineConfig({
    plugins: [
        vue(),
        vueDevTools(),
        vuetify()
    ],
})
```
Также необходимо добавить vuetify в app в **main.ts**
```ts
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { createVuetify } from 'vuetify'
import 'vuetify/styles'

const vuetify = createVuetify({})
createApp(App).use(vuetify).mount('#app')
```

Теперь можно добавлять компоненты vuetify. 
Большая часть компонентов ты можешь найти там. 
Вместо данной библиотеки порой использую другие (bootstrap - один из наиболее популярных аналогов).

Как прикрутить и настроить нужный тебе компонент vuetify ты можешь прочитать тут: 
https://dev.vuetifyjs.com/en/components/all/#navigation.
