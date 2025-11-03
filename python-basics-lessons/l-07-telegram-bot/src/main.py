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
