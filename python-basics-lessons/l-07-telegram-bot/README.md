# Создание простого телеграм бота

## Регистрация бота

Для начала нужно зарегистрировать бота в специальном телеграм боте: https://t.me/BotFather.

Для регистрации твоего бота нужно в чате с BotFather для начала вбить команду "/start".

Потом в ответном сообщении найти команду для создания бота и отправить ее (на данный момент это "/newbot").
Затем нужно следовать инструкциям BotFather бота.

При успешной регистрации тебе должен выдаться токен бота.
При помощи этого токена ты будешь связывать свое приложение с api телеграмма. 
Этот токен никому нельзя показывать.
Выглядит же токен следующим образом:
```
7139050071:AAGVkgem-GOhLRGIxuuyOSha_SoAY_fkB73
```

## Настройка зависимостей проекта

В этом уроке мы будем разрабатывать телеграм бота на основе библиотеки pytelegrambotapi.
Существует множество библиотек для разработки телеграм ботов.
Предложенная библиотека на данный момент одна из наиболее популярных на ровне с aiogram 
(большая часть функций в aiogram похожа с точностью до названий).

Для начала создадим простой python проект,
который будет состоять из одного пакета **src**.
Внутри пакета **src** будут лежать пустой **__init__.py** и **main.py** с логикой работы приложения.

Поскольку проект будет использовать сторонние зависимости
(как минимум тот же pytelegrambotapi),
для начала нужно подгрузить их в проект.
Подгружать зависимости будем с помощью библиотеки poetry.
Ее можно установить в linux с помощью команды:
```shell
curl -sSL https://install.python-poetry.org | python3
```

Файл с зависимостями **pyproject.toml** (и прочими настройками проекта)
можно создать с помощью того же poetry.
Для этого в корневой директории проекта (в данном примере корневая папка это **l1-first-endpoint**) выполним команду:
```shell
poetry init
```
Данная команда в интерактивном режиме поможет заполнить базовые настройки проекта.
Также данная команда создать директорию окружения проекта **.venv**, в которую и устанавливаются все зависимости.

Если нужно добавить зависимости уже после создания проекта, это можно сделать с помощью команды:
```shell
poetry add pytelegrambotapi pydantic-settings
```
В данном случае добавим в зависимости пакеты:
- pytelegrambotapi (библиотека для работы с telegram)
- pydantic-settings (для загрузки переменных из окружения, об этом чуть позже)

Дальше нужно установить зависимости нашего проекта:
```shell
poetry lock
poetry install
```

## Запуск простого телеграм бота

Для начала напишем простого бота, которое будет приветствовать пользователя при начале общения:
```python
import telebot

token = 'твой токен'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'help'])
def start_message(message):
    bot.reply_to(message, 'Hi 👾')
    bot.send_message(message.chat.id, 'ヾ(•ω•`)o')


bot.infinity_polling()
```
Тут:
- создается объект телеграм бота, который будет обрабатывать сообщения (```bot = telebot.TeleBot(token)```)
- происходит привязка событий прихода сообщений /start и /help через декоратор (```@bot.message_handler(commands=['start', 'help'])```)
- отправка ответа на сообщение, пришедшее от пользователя (```bot.reply_to(message, 'Hi 👾')```)
- отправка обычного сообщения (```bot.send_message(message.chat.id, 'ヾ(•ω•`)o')```).
Здесь **message.chat.id** - id чата из которого было прислано сообщение. 
При отправке сообщения на самом деле можно указывать id любого чата, который уже был начат с ботом 
(те любого пользователя, который однажды нажал '/start' в этом боте).
Таким образом можно как отвечать в текущий чат, так и делать рассылку сообщений пользователям.
- запуск бесконечной обработки дальнейших сообщений (```bot.infinity_polling()```)

Запустить приложение можно также с помощью poetry:
```shell
poetry run python src/main.py
```

Пока приложение будет работать ботом можно будет пользоваться.

### Документация команд

Чтобы у пользователя подсвечивались доступные команды и их описание, 
их можно задекларировать через BotFather через команду /setcommands.
Для этого там необходимо будет указать:
- бота, для которого предназначена команда
- саму команду
- ее описание

## Дальнейшая обработка сообщений

Также под методом обработки сообщений /start и /help можно написать блок, 
который будет обрабатывать все остальные сообщения 
и отвечать на них тем же текстом:
```python
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    print(f'Сообщение пришло от {message.from_user.username}')
    bot.reply_to(message, message.text)
```
Здесь мы воводим в консоль имя пользователя, от которого пришло сообщение 
при помощи ```message.from_user.username```.

### Форматирование сообщений

Поскольку телеграм поддерживает различные форматы разметки текста 
(такие как html и markdown), 
мы можем форматировать отправляемые сообщения.
Для этого необходимо при отправке сообщений указать формат через параметр 
**parse_mode** и отформатировать отправляемую строку текста.
Переделаем функцию обработки команд /start, чтобы она возвращала форматированные сообщения:
```python
bot.send_message(message.chat.id,
                 '*ヾ(•ω•`)o*  [ссылка на этот урок](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/python-basics-lessons/l-07-telegram-bot)',
                 parse_mode='markdown')
```

## Использование конфигов и переменных окружения

В данном проекте у нас есть переменная token, 
которую хорошо бы нигде лишний раз не светить, 
чтобы никто не получил доступ к нашему боту.
В больших же проектах у приложений существует множество настроечных переменных.
Чтобы было легче задавать такие настроечные переменные, 
их можно для начала вынести в отдельный конфиг (**src/config.py**).
Опишем настройки нашего приложения через объект унаследованный от класса BaseSettings
(из пакета **pydantic-settings**, который мы предварительно установили выше):
```python
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = ''


settings = Settings()
```

Тогда в **main.py** можно просто импортировать объект со всеми нашими настройками.
А все переменные настроек работы проекта будем получать из этого объекта 
(например так: settings.TELEGRAM_TOKEN).
Тогда создание основного объекта телеграм бота в **main.py** будет выглядеть следующим образом:
```python
from config import settings

token = settings.TELEGRAM_TOKEN
bot = telebot.TeleBot(token)
```

### Чтение переменных окружения из .env файла

Однако тут возникает проблема.
Сейчас настройки жестко вшиты в код проекта.
Чтобы проект можно было по-разному разворачивать, не меняя самого кода,
переменные обычно берутся из "окружения".
Переменные могут браться непосредственно из процесса, 
под которым работает сессия терминала,
или же из специального **.env** файла.
Запишем новое значение нашей переменной в **.env** файл.
```python
TELEGRAM_TOKEN='7139050071:AAGVkgem-GOhLRGIxuuyOSha_SoAY_fkB73'
```

Теперь добавим в **config.py** возможность чтения переменных из этого файла.
Для этого у класса настроек нужно описать специальный параметр (model_config) класса, от которого тот наследуется:
```python
from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file='.env'
    )
    TELEGRAM_TOKEN: str = ''


settings = Settings()
```

Чтобы случайно не сохранить в гите токен, 
добавим **.env** файл в список игнорируемых гитом файлов в **.gitignore**:
```gitignore
.env
```

Чтобы у других разработчиков был пример формата **.env** файла, 
можно добавить **.env.example** файл.
В **.env.example** файл можно поместить неликвидные данные, 
поскольку он все равно будет просто примером.

## Асинхронная обработка запросов

Чтобы приложение могло обрабатывать больше запросов параллельно, 
можно сделать его асинхронным.
Тогда в моменты, когда приложение ждет ответа на тот или иной запрос, 
оно будет просто переключаться на обработку другого запроса.

Для этого нам понадобиться еще пара библиотек:
```shell
poetry add asyncio aiohttp
```

Теперь мы можем переписать все методы в **main.py** на асинхронные:
```python
import asyncio

from telebot.async_telebot import AsyncTeleBot

from config import settings

token = settings.TELEGRAM_TOKEN
bot = AsyncTeleBot(token)


@bot.message_handler(commands=['start', 'help'])
async def start_message(message):
    await bot.reply_to(message, 'Hi 👾')
    await bot.send_message(message.chat.id, 'ヾ(•ω•`)o')


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    print(f'Сообщение пришло от {message.from_user.username}')
    await bot.reply_to(message, message.text)


asyncio.run(bot.polling())
```

## Кнопки

Телеграм позволяет добавлять меню с кнопкам в диалог или к конкретным сообщениям.

### Прикручивание кнопок к сообщению

Добавим кнопки к какому-нибудь сообщению.

В момент обработки сообщения от пользователя мы можем отправлять еще сообщение одно сообщения с кнопками:
```python
from telebot import types

@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    print(f'Сообщение пришло от {message.from_user.username}')
    await bot.reply_to(message, message.text)
    
    question_text = f'{message.from_user.first_name},  хочешь поговорить об этом?'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Я - бивень!', callback_data='bivenq'))
    await bot.send_message(message.chat.id, question_text, reply_markup=markup)
```
Здесь мы:
- создаем менюшку, которая будет содержать в себе кнопки 
(```markup = types.InlineKeyboardMarkup()```)
- добавляем в менюшку кнопку с текстом 'Я - бивень!' и названием события ('bivenq'), которое должно вызываться при нажатии
(```markup.add(types.InlineKeyboardButton('Я - бивень!', callback_data='bivenq'))```)
- прикручиваем эту менюшку к отправляемому сообщению при помощи параметра "reply_markup=markup"
(```await bot.send_message(message.chat.id, question_text, reply_markup=markup)```)

Чтобы обработать событие 'bivenq' необходимо добавить обработчик событий (аналогично обработчику сообщений):
```python
@bot.callback_query_handler(func=lambda callback: True)
async def callback_message(callback):
    if callback.data == 'bivenq':
        await bot.send_message(callback.message.chat.id, 'Ну ты походу бивень .. 🐘')
```
Здесь:
- привязываем обработку всех событий нажатия на кнопки к функции
(```@bot.callback_query_handler(func=lambda callback: True)```)
- проверяем, что обработанное событие называлось 'bivenq'
(```if callback.data == 'bivenq':```)
- отправляем сообщение в чат, в котором обрабатывалось данное событие
(```await bot.send_message(callback.message.chat.id, 'Ну ты походу бивень .. 🐘')```)

### Прикручивание кнопок к основному меню

Также кнопки можно прикручивать к основной менюшке (возле поля ввода текста).
Такой тип кнопок будет отправлять сообщение в чат от имени пользователя, 
после чего данное сообщение можно обрабатывать как команду.

Для этого в какой-то момент необходимо прикрутить особую разметку к сообщению.

Сделаем это в момент вызова команды '/start', чтобы кнопки были видно при первом входе в бота.
Объявление разметки с кнопками в основном меню будет выглядеть следующим образом:
```python
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add(types.KeyboardButton("Помощь"))
markup.add(types.KeyboardButton("Заказать морскую соль"))
```
Здесь:
- задана разметка для основного меню
(```types.ReplyKeyboardMarkup(resize_keyboard=True)```)
- добавлены кнопки основного меню, которые будут отправлять текст из кнопки от имени пользователя при нажатии на них
(например ```markup.add(types.KeyboardButton("Помощь"))```)

Прикрутить эту разметку нужно к методу отправки сообщении все тем же параметром "reply_markup=markup". 

Тогда новая функция обработки команды /start будет выглядеть:
```python
@bot.message_handler(commands=['start', 'help'])
async def start_message(message):
    await bot.reply_to(message, 'Hi 👾')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Помощь"))
    markup.add(types.KeyboardButton("Заказать морскую соль"))
    await bot.send_message(message.chat.id,
                           '*ヾ(•ω•`)o*  [ссылка на этот урок](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/python-basics-lessons/l-07-telegram-bot)',
                           parse_mode='markdown',
                           reply_markup=markup)
```

Пока эти кнопки просто будут отправлять сообщения в чат от имени пользователя.
Теперь обработаем сообщения от этих кнопок, переписав метод обработки сообщений:
```python
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    if message.text == "Помощь":
        await bot.send_message(message.chat.id, "Данный бот поддерживает команды /start и /help")
    elif message.text == "Заказать морскую соль":
        await bot.send_message(message.chat.id, "Не во всех телеграм ботах можно заказывать морскую соль! Тут низя ..")
    else:
        ...дальнейшая обработка обычных сообщений...
```
Т.е. тут мы просто проверяем, что пришло название кнопки из меню, 
иначе просто обрабатываем сообщения как раньше.

В остальном можно делать все манипуляции, которые позволяет телеграм 
(удалять, редактировать сообщения, отправлять картинки, стикеры, итд.).

Подробнее про работу с библиотекой **pytelegrambotapi** можно почитать тут:
https://pytba.readthedocs.io/en/latest.
