"""
Основной модуль программы телеграмм-бота.
Содержит функции, отвечающие за взаимодействие бота с пользователем:
обработка команд;
обработка любых сообщений;
обработка нажатия кнопки.
"""

import telebot
from botrequests import user_class
from typing import Any
from settings import TOKEN
import time
from loguru import logger
import json


logger.add("debug.log", level="DEBUG", rotation='10 KB', compression="zip")
logger.debug('Error')
logger.info('Information message')
logger.warning('Warning')

users = dict()
bot = telebot.TeleBot(TOKEN)
command = ['help', 'Help', 'lowprice', 'Lowprice', 'highprice', 'Highprice', 'bestdeal', 'Bestdeal', 'start', 'Start']
command_text = '/lowprice — <i>вывод самых дешёвых отелей в городе</i>' \
               '\n/highprice — <i>вывод самых дорогих отелей в городе</i>' \
               '\n/bestdeal — <i>вывод отелей, наиболее подходящих по цене и расположению</i>'


@bot.message_handler(commands=command)
def handle_command(message):
    """
    Обрабатывает команды типа '/text'
    """
    users[f"{message.chat.id}"] = [message.from_user.first_name, message.from_user.last_name]
    text = ', Давайте определимся с местом отдыха.\nВведите название города\n(Enter the name of the city): '
    if message.text == '/help' or message.text == '/Help' or message.text == '/start' or message.text == '/Start':
        bot.send_message(message.chat.id, 'Привет! Я помогу найти подходящий Вам отель.\n'
                                          '(Hey! I will help you find the hotel that suits you.)\n'
                                          'Вот перечень моих команд:\n(Here is a list of my commands:)\n'
                         + command_text, parse_mode='HTML')
    else:
        if message.text[1::] in command:
            letter = message.text[1]
            bot.send_message(message.from_user.id, str(message.from_user.first_name) + text)
            bot.register_next_step_handler(message, user_class.User(message.chat.id, bot, command_text).city_search,
                                           str(letter).lower())


@bot.message_handler(content_types=['text'])
def send_welcome(message):
    """
    Отвечает на текстовые сообщения, которые не предусмотрены в работе бота
    """
    text = user_class.translate_eng(message.text, 'Что-то пошло не так...'
                                                  '\nДавайте попробуем ещё раз.\nВот перечень моих команд:')
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, command_text, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def handle(call) -> Any:
    """
    Обработка кнопок. Информация имеет вид: 'cityP1234567l' P-для выбора языка, l -откуда пришла,
    city - подтверждает выбор пользователем города, передаёт  'P1234567l' и новый message в
    num_for_text для проверки нового message на числовое значение
    """
    city_id = call.data[4::]
    text = user_class.translate_eng(city_id, 'Какое количество отелей вывести?')
    bot.send_message(call.message.chat.id, text)
    users[f"{call.message.chat.id}"].append(city_id)
    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump(users, f)
    bot.register_next_step_handler(call.message, user_class.User(call.message.chat.id, bot,
                                                                 command_text).num_for_text, city_id)


while True:
    try:
        bot.polling(none_stop=True)
    except:
        time.sleep(15)
