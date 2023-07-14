"""
1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
сохранить JSON-вывод в файле *.json.
"""

import requests
import time
import json

# Создаём функцию получения кода страницы по URL-адресу
def get_data(url: str) -> dict:
    while True:
        time.sleep(1)
        response = requests.get(url)
        if response.status_code == 200:
            break
    return response.json()


# Формируем URL-адрес с именем пользователя
username = input('Введите username: ')
url = 'https://api.github.com/users/'+username+'/repos'


# Вызываем функцию получения кода страницы и передаём ей URL-адрес
response = get_data(url)
print()
print('Код страницы')
print(response)

# Создаём пустой список, который будем заполнять именами репозиториев по ключу 'name'
reposit_list = []
for itm in response:
    reposit_list.append(itm['name'])
print()
print(f'Список репозиториев пользователя {username}')
print(reposit_list)

with open('MCPD_lesson1_task1.json', 'w') as f:
    MCPD_lesson1_task1 = json.dump(reposit_list, f)