# Использование переменных окружения для задания настроек web приложения

[//]: # ( TODO описание зачем конфигурировать)

## Использование переменных окружения в приложении и загрузка их из .env файлов

[//]: # (TODO)

**vite.config.ts**
```ts
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd());
    return {
        plugins: [
            vue(),
            vuetify()
        ],
    }
})
```

**.env**
```
VITE_APP_GREETING_MESSAGE="Hello localhost!"
```

**.env.production**
```
VITE_APP_GREETING_MESSAGE="Hello prod!"
```

**App.vue**
```vue
<script setup lang="ts">
  import {ref} from "vue"
  const greetingMessage = ref<string>(import.meta.env.VITE_APP_GREETING_MESSAGE)
</script>

<template>
  <h1>{{ greetingMessage }}</h1>
</template>
```
