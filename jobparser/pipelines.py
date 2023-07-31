from itemadapter import ItemAdapter
from pymongo import MongoClient
import re
import numpy as np

client = MongoClient('localhost', 27017)
vacancy2707 = client.vacancy2707

# создадим функцию для обработки заработной платы
def parse_salary(salary):
    result = {'salary_min': None, 'salary_max': None, 'salary_cur': None, 'salary_conditions': None}
    # если список пустой, вернуть словарь с NaN
    if not salary:
        return {key: np.nan for key in result}
    # если список не пустой, обработать каждый элемент
    else:
        # найти элементы, которые содержат числа
        numbers = [item for item in salary if re.search(r'\d+', item)]
        # если есть два числа, то это минимальная и максимальная зарплата
        if len(numbers) == 2:
            result['salary_min'] = int(numbers[0].replace('\xa0', ''))
            result['salary_max'] = int(numbers[1].replace('\xa0', ''))
        # если есть одно число, то это либо минимальная, либо максимальная зарплата в зависимости от слова до или от
        elif len(numbers) == 1:
            number = int(numbers[0].replace('\xa0', ''))
            if 'до ' in salary:
                result['salary_max'] = number
            elif 'от ' in salary:
                result['salary_min'] = number
        # запись символа валюты и условий оплаты
        result['salary_cur'] = salary[-3].strip()
        result['salary_conditions'] = salary[-1].strip()
        # вернуть словарь с результатами
        return result


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy2707

    def process_item(self, item, spider):
        # Обработать данные о зарплате
        # salary_data = parse_salary(item['salary'])  # вызвать функцию parse_salary и передать ей список значений из столбца salary
        salary_data = parse_salary(item.pop('salary'))

        item['salary_min'] = salary_data['salary_min']  # добавить новые поля в item с результатами функции
        item['salary_max'] = salary_data['salary_max']
        item['salary_cur'] = salary_data['salary_cur']
        item['salary_conditions'] = salary_data['salary_conditions']

        collections = self.mongo_base['vacancies']
        if not collections.find_one({'_id': item['_id']}):  # проверить наличие документа с таким же _id
            #collections.insert_one(item)
            collections.insert_one(ItemAdapter(item).asdict())
        return item

"""
for doc in vacancy2707.vacancies.find({}):
    print(doc)

client.drop_database('vacancy2707')

vacancy2707.vacancies.count_documents({})
"""
