# Импортируем библиотеки
from pymongo import MongoClient
from pprint import pprint
from pymongo.errors import DuplicateKeyError
from bs4 import BeautifulSoup
import requests
import json
import hashlib
import numpy as np
# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
# которая будет добавлять только новые вакансии в вашу базу.
# ______________________________________________________________________________________________________________________

client = MongoClient('127.0.0.1', 27017)

# создадим указатели на БД
db_hh_datascientist1 = client['db_hh_datascientist1']

# создадим коллекцию
vacancies1 = db_hh_datascientist1.vacancies1

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

params = {'page': 0, 'items_on_page': 20}
url = "https://chelyabinsk.hh.ru/search/vacancy"
session = requests.Session()

# Функция заполнения добавления данных в коллекцию
def fillig_result_df(salary, vacancy_name, vacancy_link, company_name, company_city, vacancies1):
    if '\u2013' in salary:  # проверяем, есть ли тире в строке salary
        salary = salary.replace('\u202f', '')  # убираем неразрывные пробелы
        min_salary, max_salary = salary.split(' – ')  # разделяем по тире
        max_salary, currency = max_salary.split(' ')  # разделяем по пробелу

        # заполним словарь с данными вакансии
        doc = {'vacancy_name': [vacancy_name], 'min_salary': [int(min_salary)], 'max_salary': [int(max_salary)],
               'currency': [currency], 'company_name': [company_name], 'company_city': [company_city],
               'vacancy_link': [vacancy_link], 'website': 'https://chelyabinsk.hh.ru'}

        # на основе данных вакансии создадим id
        doc_str = json.dumps(doc, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        doc_id = hashlib.md5(doc_str.encode()).hexdigest()
        doc_final = {}
        doc_final['_id'] = doc_id
        doc_final.update(doc)
        # добавим документ doc_final в БД
        try:
            vacancies1.insert_one(doc_final)
        except DuplicateKeyError:
            print(f'Document with id {doc_final.get("_id")} already exists')

    elif 'от' in salary:  # проверяем, есть ли 'от' в строке salary
        salary = salary.replace('\u202f', '')
        salary = salary[3:]
        min_salary, currency = salary.split(' ')
        # max_salary = np.nan
        doc = {'vacancy_name': [vacancy_name], 'min_salary': [int(min_salary)], 'max_salary': np.nan,
               'currency': [currency], 'company_name': [company_name], 'company_city': [company_city],
               'vacancy_link': [vacancy_link], 'website': 'https://chelyabinsk.hh.ru'}

        # на основе данных вакансии создадим id
        doc_str = json.dumps(doc, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        doc_id = hashlib.md5(doc_str.encode()).hexdigest()
        doc_final = {}
        doc_final['_id'] = doc_id
        doc_final.update(doc)
        # добавим документ doc_final в БД
        try:
            vacancies1.insert_one(doc_final)
        except DuplicateKeyError:
            print(f'Document with id {doc_final.get("_id")} already exists')

    elif 'до' in salary:  # проверяем, есть ли 'до' в строке salary
        salary = salary.replace('\u202f', '')
        salary = salary[3:]
        max_salary, currency = salary.split(' ')
        # заполним словарь с данными вакансии
        doc = {'vacancy_name': [vacancy_name], 'min_salary': np.nan, 'max_salary': [int(max_salary)],
               'currency': [currency], 'company_name': [company_name], 'company_city': [company_city],
               'vacancy_link': [vacancy_link], 'website': 'https://chelyabinsk.hh.ru'}

        # на основе данных вакансии создадим id
        doc_str = json.dumps(doc, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        doc_id = hashlib.md5(doc_str.encode()).hexdigest()
        doc_final = {}
        doc_final['_id'] = doc_id
        doc_final.update(doc)
        # добавим документ doc_final в БД
        try:
            vacancies1.insert_one(doc_final)
        except DuplicateKeyError:
            print(f'Document with id {doc_final.get("_id")} already exists')

    elif 'NaN' in salary:  # проверяем, есть ли 'NaN' в строке salary
        # заполним словарь с данными вакансии
        doc = {'vacancy_name': [vacancy_name], 'min_salary': np.nan, 'max_salary': np.nan,
               'currency': np.nan, 'company_name': [company_name], 'company_city': [company_city],
               'vacancy_link': [vacancy_link], 'website': 'https://chelyabinsk.hh.ru'}

        # на основе данных вакансии создадим id
        doc_str = json.dumps(doc, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        doc_id = hashlib.md5(doc_str.encode()).hexdigest()
        doc_final = {}
        doc_final['_id'] = doc_id
        doc_final.update(doc)
        # добавим документ doc_final в БД
        try:
            vacancies1.insert_one(doc_final)
        except DuplicateKeyError:
            print(f'Document with id {doc_final.get("_id")} already exists')


articles_list = []
while True:
    # Точка входа на первую страницу
    response = session.get(url + '?text=data+scientist', params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    # Находим все контейнеры с вакансиями на странице
    articles = soup.find_all('div', {'class': 'serp-item'})

    # Проверяем статус-код страницы и наличие вакансий на странице
    if (response.status_code != 200) or (not articles):
        break

    for article in articles:
        info1 = article.find('a', {'class': 'serp-item__title'})
        vacancy_name = info1.text
        vacancy_link = info1.get('href')
        salary_info = article.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        info2 = article.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
        company_name = info2.text
        info3 = article.find('div', {'data-qa': 'vacancy-serp__vacancy-address'})
        company_city = info3.text
        try:
            salary = salary_info.text
            fillig_result_df(salary, vacancy_name, vacancy_link, company_name, company_city, vacancies1)
        except:
            salary = 'NaN'
            fillig_result_df(salary, vacancy_name, vacancy_link, company_name, company_city, vacancies1)
            continue

    params['page'] += 1

for doc in vacancies1.find({}):
    pprint(doc)

# подсчитаем количество вакансий в БД
vacancies_count = vacancies1.count_documents({})
print(f'Вакансий в базе: {vacancies_count}')


# ______________________________________________________________________________________________________________________
# ______________________________________________________________________________________________________________________
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы
# (необходимо анализировать оба поля зарплаты, то есть цифра вводится одна, а запрос проверяет оба поля)
# ______________________________________________________________________________________________________________________


# нижняя граница зарплаты в рублях
min_lim_salary_RUB = 100000 # '₽'

# текущие курсы валют
USD_course = 91.2  # '$'
EUR_course = 102.44  # '€'
KZT_course = 0.20319  # '₸'

# пересчёт нижней границы из рублей в валюту
min_lim_salary_USD = min_lim_salary_RUB / USD_course
min_lim_salary_EUR = min_lim_salary_RUB / EUR_course
min_lim_salary_KZT = min_lim_salary_RUB / KZT_course

# поиск информации о вакансиях с зарплатами выше чем установленный лимит
for doc in vacancies1.find({'$or': [
    {['currency'][0]: '₽', 'min_salary': {'$gt': min_lim_salary_RUB}, 'max_salary': {'$gt': min_lim_salary_RUB}},
    {['currency'][0]: '₽', 'min_salary': np.nan, 'max_salary': {'$gt': min_lim_salary_RUB}},
    {['currency'][0]: '₽', 'min_salary': {'$gt': min_lim_salary_RUB}, 'max_salary': np.nan},
    {['currency'][0]: '$', 'min_salary': {'$gt': min_lim_salary_USD}, 'max_salary': {'$gt': min_lim_salary_USD}},
    {['currency'][0]: '$', 'min_salary': np.nan, 'max_salary': {'$gt': min_lim_salary_USD}},
    {['currency'][0]: '$', 'min_salary': {'$gt': min_lim_salary_USD}, 'max_salary': np.nan},
    {['currency'][0]: '€', 'min_salary': {'$gt': min_lim_salary_EUR}, 'max_salary': {'$gt': min_lim_salary_EUR}},
    {['currency'][0]: '€', 'min_salary': np.nan, 'max_salary': {'$gt': min_lim_salary_EUR}},
    {['currency'][0]: '€', 'min_salary': {'$gt': min_lim_salary_EUR}, 'max_salary': np.nan},
    {['currency'][0]: '₸', 'min_salary': {'$gt': min_lim_salary_KZT}, 'max_salary': {'$gt': min_lim_salary_KZT}},
    {['currency'][0]: '₸', 'min_salary': np.nan, 'max_salary': {'$gt': min_lim_salary_KZT}},
    {['currency'][0]: '₸', 'min_salary': {'$gt': min_lim_salary_KZT}, 'max_salary': np.nan}]}):
    pprint(doc)

client.close()






