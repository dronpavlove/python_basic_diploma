"""
Судя по всему поменяли работу API. Возвращаются словари с другим содержимым.
Надо менять логику программы.
Я вижу, что сейчас достаточно ввести НАЗВАНИЕ ГОРОДА и можно сразу получить список отелей
"""

import requests
import json
import pprint

headers_dict = {
    'X-RapidAPI-Key': '',
    'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
  }
url = "https://hotels4.p.rapidapi.com/locations/search"
querystring = {"query": "Москва", "locale": "ru_RU"}
response = requests.get(url, headers=headers_dict, params=querystring)
new_data = json.loads(response.text)
print("============Это результат полного запроса:=============")
pprint.pprint(new_data)

print("============Так можно сразу получить инфу об отелях в городе:=============")
print("Город в запросе: ", new_data['term'])
hotels_list = [i['entities'] for i in new_data['suggestions'] if len(i['entities']) > 0]
for num in range(len(hotels_list)):
    for i in hotels_list[num]:
        print(i['name'])

# for elem in new_data['suggestions']:
#     try:
#         pprint.pprint(elem['entities'])
#         hotels_data = {i['name']: i['destinationId'] for i in elem['entities']}
#         print(hotels_data)
#     except:
#         pass
