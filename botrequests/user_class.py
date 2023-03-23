"""Модуль содержит класс User"""

import re
from telebot import types
from botrequests import class_for_bot


class User:
    """
    Класс, отвечающий за взаимодействие с отдельным пользователем.
    Пинимает id-пользователя, сгенерированного бота и текстовую конструкцию для ответов.
    """
    def __init__(self, chat_id, bot, command_text: str):
        self.chat_id = chat_id
        self.bot = bot
        self.command_text = command_text

    def city_search(self, message, letter: str):
        """
        Метод по названию города возвращает кнопки из найденных городов, название которых схоже с искомым.
        В callback_data передаётся destinationId города плюс буква от названия города (для определения языка)
        и плюс литера, указывающая на изначальную цель поиска: 'cityP1234567l'
        """
        text = translate_eng(message.text, f"Веду поиск в городе {message.text}, надо подождать...")
        self.bot.send_message(self.chat_id, text)
        count = 0
        markup = types.InlineKeyboardMarkup()
        for city in class_for_bot.City(message.text).city_search():
            count += 1
            button = types.InlineKeyboardButton(city['call_name'], callback_data='city' + city['call_name'][0] +
                                                                                 city['call_result']['destinationId'] +
                                                                                 letter)
            markup.row(button)
        if count > 0:
            text = translate_eng(message.text, "Выберите объект поиска:")
            self.bot.send_message(self.chat_id, text, reply_markup=markup)
        else:
            text = translate_eng(message.text, "Видимо проблемы с поиском. Попробуем ещё раз:")
            self.bot.send_message(self.chat_id, text)
            self.bot.send_message(self.chat_id, self.command_text, parse_mode='HTML')

    def price_distance(self, message, city_id):
        """
        Метод запрашивает у пользователя удаленность, минимальную и максимальную стоимость.
        Полученные ответы проверяет на ввод цифрами.
        Возвращает строку вида: 2 7 4 5 М1153093b, где 2- удаленность, 7- макс. цена
                                                           4- миним. цена, 5- кол. отелей
                                                           М1153093b- ID города с литерами
        :param message: message
        :param city_id: str
        :return: str
        """
        city_id = message.text + ' ' + city_id
        landmark = len(city_id.split(' '))
        if landmark == 2:
            text = translate_eng(city_id, 'Минимальная цена:')
            self.bot.send_message(self.chat_id, text)
            self.bot.register_next_step_handler(message, self.num_for_text, city_id)
        elif landmark == 3:
            text = translate_eng(city_id, 'Максимальная цена:')
            self.bot.send_message(self.chat_id, text)
            self.bot.register_next_step_handler(message, self.num_for_text, city_id)
        elif landmark == 4:
            text = translate_eng(city_id, 'Удалённость от центра:')
            self.bot.send_message(self.chat_id, text)
            self.bot.register_next_step_handler(message, self.num_for_text, city_id)
        elif landmark == 5:
            self.hotel_search(message, city_id)

    def num_for_text(self, message, city_id):
        """
        Метод добивается от пользователя ввода текста из цифр.
        Передаёт результат в функцию поиска отелей.
        """
        if message.text.replace('.', '').isdigit():
            if city_id[-1] != 'b':
                self.hotel_search(message, city_id)
            else:
                self.price_distance(message, city_id)
        else:
            text = translate_eng(city_id, 'Вводите цифрами, если десятичные- то с точкой: 12.32')
            self.bot.send_message(self.chat_id, text)
            self.bot.register_next_step_handler(message, self.num_for_text, city_id)

    def hotel_search(self, message, city_id: str):
        """
        Метод поиска отелей по заданным характеристикам.
        Если city_id[-1] это 'l', 'h', 'b', то возвращает сообщения
        в заданном количестве (message) в заданной последовательности ('l' - по убыванию стоимости,
        'h' - по возрастанию стоимости, 'b' - по удалённости в заданном диапозоне цен)
        """
        sort_object = tuple()
        counter = 0
        text = translate_eng(city_id, "Веду поиск, надо подождать...")
        self.bot.send_message(message.chat.id, text)
        if city_id[-1] == 'l' or city_id[-1] == 'h':
            num = int(message.text)
            sort_object = class_for_bot.City(city_id).hotel_sort(amount=num)
        if city_id[-1] == 'b':
            info_list = city_id.split(' ')
            sort_object = class_for_bot.City(info_list[4]).hotel_sort(int(info_list[3]), info_list[:3:])
        for hotel in sort_object:
            text_1, text_2 = translate_eng(city_id, "Адрес: "), translate_eng(city_id, "стоимость: ")
            text_3, text_4 = translate_eng(city_id, "класс: "), translate_eng(city_id, "удалённость: ")
            text_5 = translate_eng(city_id, "фото")
            text = '<b>' + str(hotel[0]) + '</b>' + '\n<b>' + text_1 + '</b>' + \
                   '<i>' + str(hotel[1]['street']) + '</i>' + \
                   '\n<b>' + text_2 + '</b>' + '<i>' + str(hotel[1]['exactCurrent']) + '</i>' + \
                   '\n<b>' + text_3 + '</b>' + '<i>' + str(hotel[1]['starRating']) + '</i>' + \
                   '\n<b>' + text_4 + '</b>' + '<i>' + str(hotel[1]['distance']) + '</i>' + \
                   '\n<a href="' + str(hotel[1]['URL']) + '">' + text_5 + '</a>'
            self.bot.send_message(self.chat_id, text, parse_mode='HTML')
            counter += 1
        if counter > 0:
            text = translate_eng(city_id, "Если хотите продолжить, воспользуйтесь командами")
            self.bot.send_message(self.chat_id, text + ":\n" + self.command_text, parse_mode='HTML')
        else:
            text = translate_eng(city_id, "Видимо, в этом городе нет известных нам отелей...")
            self.bot.send_message(self.chat_id, text + ":\n" + self.command_text, parse_mode='HTML')


def translate_eng(word, text):
    data_word = {
        "Если хотите продолжить, воспользуйтесь командами": "If you want to continue, use the commands",
        "Видимо, в этом городе нет известных нам отелей...": "Apparently, there are no hotels known to us in this city ...",
        "Веду поиск, надо подождать...": "Searching, gotta wait...",
        'Вводите цифрами, если десятичные- то с точкой: 12.32': 'Enter in numbers, if decimal- then with a dot: 12.32...',
        'Минимальная цена:': 'Minimum price:',
        'Максимальная цена:': 'Maximum price:',
        'Удалённость от центра:': 'Distance from the center:',
        "Выберите объект поиска:": "Select search object:",
        "Видимо проблемы с поиском. Попробуем ещё раз:": "Apparently there are problems with the search. Let's try again:",
        "Адрес: ": "Address: ",
        "стоимость: ": "price: ",
        "класс: ": "stars: ",
        "фото": "foto",
        "удалённость: ": "remoteness: ",
        'Какое количество отелей вывести?': 'How many hotels should you withdraw?',
        'Что-то пошло не так...\nДавайте попробуем ещё раз.\nВот перечень моих команд:':
            'Something went wrong...\nLet"s try again.\nHere is a list of my commands:'
    }
    leng = word.split(' ')[-1][0]
    if not re.search(r'[А-Яа-я]', leng):
        try:
            text = data_word[text]
        except:
            pass
    return text

