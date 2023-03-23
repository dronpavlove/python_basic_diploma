"""
Модуль содержит класс City, функцию except_write - обработка ошибок
и info_data - база донных с id-пользователя и id-запроса
"""

import json
import requests
import re
import datetime
from settings import headers_dict


class City:
    """
    Класс взаимодействия запросов с сайтом API
    """
    __headers = headers_dict

    def __init__(self, city_info):
        self.city_info = city_info
        if re.search(r'[A-Za-z]', self.city_info[0]):
            self.lang = 'en_US'
            self.currency = 'USD'
        else:
            self.lang = 'ru_RU'
            self.currency = 'RUB'

    def set_headers(self, headers_dict):
        """Изменение ключей доступа к сайту API"""
        self.__headers = headers_dict

    def city_search(self) -> tuple:
        """
        Метод возвращает tuple в виде словарей, в которых
        call_name - текст для кнопки,
        call_result - словарь значений для города
        """

        url = "https://hotels4.p.rapidapi.com/locations/search"
        querystring = {"query": self.city_info, "locale": self.lang}
        headers = self.__headers
        # теперь здесь сразу возвращает список городов с совпавшим названием
        try:
            response = requests.get(url, headers=headers, params=querystring)
            data_deaths = json.loads(response.text)
            query_list = [i['entities'] for i in data_deaths['suggestions'] if len(i['entities']) > 0]  # ["suggestions"][0]["entities"]
            city_list = []
            hotels_list = []  # этот здесь лишний
            for num in range(len(query_list)):
                for i in query_list[num]:
                    if i['type'] == 'CITY':
                        city_list.append(i)
                    elif i['type'] == 'HOTEL':
                        hotels_list.append(i)

            for city in city_list:
                yield {'call_name': city['name'], 'call_result': city}

        except KeyError:
            return None

    @staticmethod
    def clear_text(text) -> str:
        """
        Очищает текст от тегов
        """
        text_list = [word for word in text.split(', ')]
        result = ''
        for word in text_list:
            if word.startswith('<'):
                result += re.findall(r'>\w+', word)[0][1::] + ', '
            else:
                result += word + ', '
        return result[:-2:]

    def hotel_search(self) -> dict:
        """
        Метод возвращает словарь отелей по ID города 'Р1173889'
        (буква берётся из названия города для определения locale):
        City('Р1173889').hotel_search()->
        'Хостел Orange': {'distance': '1,9 км',
                   'exactCurrent': 12.31,
                   'starRating': 2.0,
                   'street': 'ул. Московская, 68'}
        """
        check = datetime.date.today()
        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {
            "adults1": "1",
            "pageNumber": "1",
            "destinationId": self.city_info[1:-1:],  # потому что строка вида "P1153093l", Р-для выбора языка, l -откуда
            "pageSize": "25",
            "checkOut": check,
            "checkIn": check,
            "sortOrder": "PRICE",
            "locale": self.lang,  # "ru_RU",
            "currency": self.currency  # 'USD'
        }
        headers = self.__headers
        data = dict()
        try:
            response = requests.request("GET", url, headers=headers, params=querystring)
            full_info_list = json.loads(response.text)['data']['body']['searchResults']['results']
            for elem in full_info_list:
                key = elem['name']
                data[key] = dict()
                try:
                    data[key]['street'] = elem['address']['streetAddress']
                except KeyError:
                    data[key]['street'] = elem['address']
                try:
                    data[key]['starRating'] = elem['starRating']
                except KeyError:
                    data[key]['starRating'] = 'None'
                try:
                    data[key]['exactCurrent'] = elem['ratePlan']['price']['exactCurrent']
                except KeyError:
                    data[key]['exactCurrent'] = 'None'
                try:
                    data[key]['URL'] = elem['optimizedThumbUrls']['srpDesktop']
                except KeyError:
                    data[key]['URL'] = 'None'
                try:
                    data[key]['distance'] = elem['landmarks'][0]['distance']
                except KeyError:
                    data[key]['distance'] = '50 km'
            return data
        except KeyError:
            return data

    def hotel_sort(self, amount=10, *args):
        """
        Метод возвращает кортеж отсортированных по заданным параметрам словарей
        """
        price_list = []
        hotel_dict = self.hotel_search()
        for key in hotel_dict:
            if hotel_dict[key]['exactCurrent'] != 'None' \
                    and not hotel_dict[key]['exactCurrent'] in price_list:
                price_list.append(hotel_dict[key]['exactCurrent'])
        if self.city_info[-1] == 'l':
            sort_price_list = sorted(price_list)
        else:
            sort_price_list = sorted(price_list)[::-1]
        if amount > len(price_list):
            amount = len(price_list)
        if self.city_info[-1] == 'l' or self.city_info[-1] == 'h':
            for price in sort_price_list:
                for elem in hotel_dict:
                    if hotel_dict[elem]['exactCurrent'] == price and amount != 0:
                        amount -= 1
                        yield elem, hotel_dict[elem]
        else:
            dist = float(args[0][0])
            max_price = float(args[0][1])
            min_price = float(args[0][2])
            if max_price < min_price:
                max_price, min_price = min_price, max_price
            for elem in hotel_dict:
                try:
                    if num_from_str(hotel_dict[elem]['distance']) < dist \
                            and hotel_dict[elem]['exactCurrent'] != 'None'\
                            and min_price < hotel_dict[elem]['exactCurrent'] < max_price \
                            and amount != 0:
                        amount -= 1
                        yield elem, hotel_dict[elem]
                except:
                    pass


def num_from_str(text: str) -> float:
    num_text = ''
    for letter in text:
        if letter.isdigit():
            num_text += letter
        elif letter == ',' or letter == '.':
            num_text += '.'
    return float(num_text)
