# Вариант I
# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные
# о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)
# Логин тестового ящика: study.ai_172@mail.ru
# Пароль тестового ящика: NextPassword172#
#_______________________________________________________________________________________________________________________

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
import json
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
import hashlib
from pprint import pprint


chromeOptions = Options()
chromeOptions.add_argument('start-maximized')

# зайдём на страницу ввода пароля
s = Service('./chromedriver.exe')
drv = webdriver.Chrome(service=s, options=chromeOptions)
drv.implicitly_wait(5)

drv.get('https://account.mail.ru')
time.sleep(1)

# введём логин
elem = WebDriverWait(drv, 5).until(
    EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
elem.send_keys("study.ai_172")


# активируем кнопку "Ввести пароль"
elem = drv.find_element(
    By.XPATH, "//button[@data-test-id='next-button']")
elem.click()
time.sleep(1)

# введём пароль
elem = WebDriverWait(drv, 5).until(
    EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
elem.send_keys("NextPassword172#")
time.sleep(1)

# активируем кнопку "Войти"
elem.send_keys(Keys.ENTER)

# перейдём во входящие письма
elem = WebDriverWait(drv, 5).until(
    EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'nav__item_active')]")))

# определим количество входящих писем
mail_cnt = int(elem.get_attribute("title").split()[1])

print()

mails_link_set = set() # множество для хранения писем
last_elem = None

while len(mails_link_set) < mail_cnt:
    # находим контейнеры писем
    mails = WebDriverWait(drv, 5).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'llc')]")))
    # заполняем множество найденных писем
    mails_link = [mail.get_attribute("href") for mail in mails]
    mails_link_set = mails_link_set.union(set(mails_link))
    # переходим к последнему элементу и подтверждаем действие
    actions = ActionChains(drv)
    actions.move_to_element(mails[-1])
    actions.perform()
    time.sleep(0.5)

client = MongoClient('127.0.0.1', 27017)
# создадим указатели на БД
db_mail_ru_letters = client['db_lenta_ru_letters']
# создадим коллекцию
letters_collection = db_mail_ru_letters.letters
session = requests.Session()

# создадим и заполним общий список информации по письмам
mails_info = []
for mail_link in mails_link_set:
    if isinstance(mail_link, str):
        mail_info = {}
        drv.get(mail_link)

        mail_source = WebDriverWait(drv, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "letter__author")))

        mail_author = mail_source.find_element(
            By.XPATH, ".//span[@class='letter-contact']")
        mail_info["author"] = f"{mail_author.text} {mail_author.get_attribute('title')}"

        mail_date = mail_source.find_element(
            By.XPATH, ".//div[@class='letter__date']")
        mail_info["date"] = mail_date.text

        mail_thread = drv.find_element(
        By.XPATH, "//h2[@class='thread-subject']")
        mail_info["thread"] = mail_thread.text

        mail_text = WebDriverWait(drv, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='letter__body']")))
        mail_info["text"] = mail_text.text

        # на основе данных письма создадим id
        letters_str = json.dumps(mail_info, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        letters_id = hashlib.md5(letters_str.encode()).hexdigest()
        letters_final = {}
        letters_final['_id'] = letters_id
        letters_final.update(mail_info)

        # добавим документ letters_final в БД
        try:
            letters_collection.insert_one(letters_final)
        except DuplicateKeyError:
            print(f'Document with id {letters_final.get("_id")} already exists')

        mails_info.append(mail_info)

for letters in letters_collection.find({}):
    pprint(letters)

# подсчитаем количество писем в БД
letters_count = letters_collection.count_documents({})

print(f'Писем в базе: {letters_count}')

client.close()
