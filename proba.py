"""
Судя по всему поменяли работу API. Возвращаются словари с другим содержимым.
Надо менять логику программы.
Я вижу, что сейчас достаточно ввести НАЗВАНИЕ ГОРОДА и можно сразу получить список отелей
"""
import time

import requests
import json
import pprint
import datetime

headers_dict = {
    'X-RapidAPI-Key': '5bbb5c2f65msh17b2cb03b4c6553p19e639jsnbfe2564f778f',
    'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
  }
url = "https://hotels4.p.rapidapi.com/locations/search"
querystring = {"query": "Брест", "locale": "ru_RU"}
response = requests.get(url, headers=headers_dict, params=querystring)
new_data = json.loads(response.text)
print("============Это результат полного запроса:=============")
pprint.pprint(new_data)

print("============Так можно сразу получить инфу об отелях в городе:=============")
print("Город в запросе: ", new_data['term'])
query_list = [i['entities'] for i in new_data['suggestions'] if len(i['entities']) > 0]
city_list = []
hotels_list = []
for num in range(len(query_list)):
    for i in query_list[num]:
        if i['type'] == 'CITY':
            city_list.append(i)
        elif i['type'] == 'HOTEL':
            hotels_list.append(i)
for city in city_list:
    print(city['name'], city['destinationId'])
print(hotels_list)

# Дольше url = "https://hotels4.p.rapidapi.com/properties/list" сюда запрос у меня не работает в
# class_for_bot hotel_search
