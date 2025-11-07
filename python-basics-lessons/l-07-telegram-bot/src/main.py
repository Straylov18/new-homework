import asyncio

from telebot.async_telebot import AsyncTeleBot
from telebot import types

from config import settings

token = settings.TELEGRAM_TOKEN
bot = AsyncTeleBot(token)


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


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    if message.text == "Помощь":
        await bot.send_message(message.chat.id, "Данный бот поддерживает команды /start и /help")
    elif message.text == "Заказать морскую соль":
        await bot.send_message(message.chat.id, "Не во всех телеграм ботах можно заказывать морскую соль! Тут низя ..")
    else:
        print(f'Сообщение пришло от {message.from_user.username}')
        await bot.reply_to(message, message.text)
        question_text = f'{message.from_user.first_name},  хочешь поговорить об этом?'
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Я - бивень!', callback_data='bivenq'))
        markup.row(types.InlineKeyboardButton('Да', callback_data='da'),
                   types.InlineKeyboardButton('Нет', callback_data='no'))
        await bot.send_message(message.chat.id, question_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
async def callback_message(callback):
    if callback.data == 'da':
        await bot.send_message(callback.message.chat.id, 'А я не хочу 🦐')
    elif callback.data == 'no':
        await bot.send_message(callback.message.chat.id, 'Ну и ладно!')
    else:
        await bot.send_message(callback.message.chat.id, 'Ну ты походу бивень .. 🐘')


asyncio.run(bot.polling())
