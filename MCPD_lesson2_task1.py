import pandas as pd

pd.set_option('display.max_columns', None)  # показывать все колонки
pd.set_option('display.width', None)  # автоматически определяем шинину окна

from bs4 import BeautifulSoup
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
params = {'page': 0}
url = "https://chelyabinsk.hh.ru/search/vacancy"
session = requests.Session()

result_df = pd.DataFrame(
    columns=['vacancy_name', 'min_salary', 'max_salary', 'currency', 'company_name', 'company_city', 'vacancy_link',
             'website'])


# Функция заполнения результирующего датафрейма
def fillig_result_df(salary, vacancy_name, vacancy_link, company_name, company_city, result_df):
    if '\u2013' in salary:  # проверяем, есть ли тире в строке salary
        salary = salary.replace('\u202f', '')  # убираем неразрывные пробелы
        min_salary, max_salary = salary.split(' – ')  # разделяем по тире
        max_salary, currency = max_salary.split(' ')  # разделяем по пробелу
        new_row = pd.DataFrame({'vacancy_name': [vacancy_name], 'min_salary': [min_salary], 'max_salary': [max_salary],
                                'currency': [currency], 'company_name': [company_name], 'company_city': [company_city],
                                'vacancy_link': [vacancy_link], 'website': 'https://chelyabinsk.hh.ru'})
        result_df = pd.concat([result_df, new_row], ignore_index=True)
    elif 'от' in salary:  # проверяем, есть ли тире в строке 'от'
        salary = salary.replace('\u202f', '')
        salary = salary[3:]
        min_salary, currency = salary.split(' ')
        new_row = pd.DataFrame({'vacancy_name': [vacancy_name], 'min_salary': [min_salary], 'currency': [currency],
                                'company_name': [company_name], 'company_city': [company_city],
                                'vacancy_link': [vacancy_link], 'website': 'https://chelyabinsk.hh.ru'})
        result_df = pd.concat([result_df, new_row], ignore_index=True)
    elif 'до' in salary:  # проверяем, есть ли тире в строке 'до'
        salary = salary.replace('\u202f', '')
        salary = salary[3:]
        max_salary, currency = salary.split(' ')
        new_row = pd.DataFrame({'vacancy_name': [vacancy_name], 'max_salary': [max_salary], 'currency': [currency],
                                'company_name': [company_name], 'company_city': [company_city],
                                'vacancy_link': [vacancy_link], 'website': 'https://chelyabinsk.hh.ru'})
        result_df = pd.concat([result_df, new_row], ignore_index=True)
    elif 'NaN' in salary:  # проверяем, есть ли тире в строке 'NaN'
        new_row = pd.DataFrame(
            {'vacancy_name': [vacancy_name], 'company_name': [company_name], 'company_city': [company_city],
             'vacancy_link': [vacancy_link], 'website': 'https://chelyabinsk.hh.ru'})
        result_df = pd.concat([result_df, new_row], ignore_index=True)
    return result_df


articles_list = []
while True:
    # Точка входа на первую страницу
    response = session.get(url + '?text=data+scientist', params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Находим все контейнеры с вакансиями на странице
    articles = soup.find_all('div', {'class': 'serp-item'})
    if not articles:
        break

    for article in articles:
        info1 = article.find('a', {'class': 'serp-item__title'})
        vacancy_name = info1.text
        vacancy_link = info1.get('href')
        parent_all = info1.parent.parent.parent
        salary_info = parent_all.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        info2 = article.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
        company_name = info2.text
        info3 = article.find('div', {'data-qa': 'vacancy-serp__vacancy-address'})
        company_city = info3.text
        try:
            salary = salary_info.text
            result_df = fillig_result_df(salary, vacancy_name, vacancy_link, company_name, company_city, result_df)
        except:
            salary = 'NaN'
            result_df = fillig_result_df(salary, vacancy_name, vacancy_link, company_name, company_city, result_df)
            continue

    params['page'] += 1

print(result_df)
# Запишем датафрейм submit в csv-файл и json-файл
result_df.to_csv('result_df.csv', index=False, encoding='utf-8')
result_df.to_json('result_df.json')
