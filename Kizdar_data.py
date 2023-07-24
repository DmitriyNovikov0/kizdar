import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from os import path
import sys
import datetime
import re
import csv

class Kizdar_data:
    FILENAME = "streetwalkers.csv"
    feya_profile = []

    def __init__(self, url_site = 'https://kyz6dar-mibe.xyz', browser = 'firefox', test = False, hideBrouser = True):
        self.__url = url_site
        self.__current_date = datetime.datetime.now().strftime("%Y.%m.%d")
        parent_dir = path.dirname(path.abspath(__file__))
        if test:
            return
        if browser == 'firefox':
            #поднастроим firfox :) - скроем автоматизацию
            option = webdriver.FirefoxOptions()
            option.set_preference('dom.webdriver.enabled', False)
            option.set_preference('dom.webnotification.enabled', False)
            option.headless = hideBrouser
            option.set_preference('general.useragent.override', 'hello :)')
            #проверим разрядность ОС
            if sys.maxsize > 2**32:
                self.__browser = webdriver.Firefox(executable_path = parent_dir + '\\drivers\\geckodriver_x64.exe', options=option)
            else:
                self.__browser = webdriver.Firefox(executable_path = parent_dir + '\\drivers\\geckodriver_x86.exe', options=option)
        else:
            self.__browser = webdriver.Chrome(executable_path = parent_dir + '\\drivers\\chromedriver.exe')

    def __open_page_site(self, page_nmb = 1):
        try:
            self.__browser.get(self.__url + '/prostitutki/almaty/' + str(page_nmb))
            return True
        except:
            pass
            #print(f'Ошибка открытия сайта {self.__url}' )

    def profile_analiysis(self, profile):
        f_href = profile.find('a', class_ = 'white').get('href')
        result = {
                  'f_id': f_href.replace('/anketa/', ''),
                  'date': self.__current_date,
                  'is_work': True,
                  'f_href': self.__url + f_href,
                  'f_name': profile.find('span', class_ = 'name').get_text(strip=True),
                  }
        f_phone = profile.find('a', class_='tel')
        if f_phone is None:
            result['is_work'] = False
        else:
            result['phone'] = f_phone.get_text(strip=True)
        #для работает или нет разобраться там через div
        # f_phone_box = profile.find('div', class_ = 'phone-box acenter')
        # f_phone = f_phone_box.find('a', class_='tel').get_text(strip=True)

        f_parametrs = profile.findAll('div', class_ = 'fastdata')
        for f_parametr in f_parametrs:
            tmp = f_parametr.contents
            if 'рост' in tmp[0].lower():
                result['height'] = tmp[1].get_text(strip=True)
                result['height_с'] = re.sub(r'[^0-9.]+', r'', result['height'])
            elif 'возраст' in tmp[0].lower():
                result['age'] = tmp[1].get_text(strip=True)
            if 'вес' in tmp[3].lower():
                result['weight'] = tmp[4].get_text(strip=True)
                result['weight_с'] = re.sub(r'[^0-9.]+', r'', result['weight'])
            elif 'нация' in tmp[3].lower():
                result['nation'] = tmp[4].get_text(strip=True)
            if 'грудь' in tmp[6].lower():
                result['breasts'] = tmp[7].get_text(strip=True)
            elif 'город' in tmp[6].lower():
                result['city'] = tmp[7].get_text(strip=True)

        f_price_table = profile.find('table', class_ = 'pricetable')
        # headers = [header.get_text(strip=True) for header in f_price_table.find('thead').findAll('th')]
        for row in f_price_table.find('tbody').findAll('tr'):
            f_price = [price.get_text(strip=True) for price in row.findAll('td')]
            place = row.find('th').get_text(strip=True).lower()
            if 'себя' in place:
                result.update({'home_contact': re.sub(r'[^0-9.]+', r'', f_price[0]), 'home_houer': re.sub(r'[^0-9.]+', r'', f_price[1])})
            elif 'выезд' in place:
                result.update({'leave_contact': re.sub(r'[^0-9.]+', r'', f_price[0]), 'leave_houer': re.sub(r'[^0-9.]+', r'', f_price[1])})
            elif 'сауне' in place:
                result.update({'sauna_contact': re.sub(r'[^0-9.]+', r'', f_price[0]), 'sauna_houer': re.sub(r'[^0-9.]+', r'', f_price[1])})
            elif 'машине' in place:
                result.update({'car_contact': re.sub(r'[^0-9.]+', r'', f_price[0]), 'car_houer': re.sub(r'[^0-9.]+', r'', f_price[1])})

        additional_info_ = profile.findAll('div', class_ = 'white')
        additional_info = ''
        for a_i in additional_info_:
            for info in a_i:
                additional_info += info.get_text(strip=True) +  '; '
        result['add_info'] = additional_info

        # f_services = profile.find('div', class_ = 'gold')
        f_services = profile.find('ul')
        services = ''
        for f_service in f_services.findAll('li'):
            services += f_service.get_text(strip=True) + '; '
        result['services'] = services

        f_service = [f_service.strip() for f_service in result['services'].split(';')]
        result['classic_sex'] = 1 if 'Классика' in f_service else -1
        result['anal_sex'] = 1 if 'Анальный секс' in f_service else -1
        result['b_with_condom'] = 1 if 'Минет с резинкой' in f_service else -1
        result['b_without_condom'] = 1 if 'Минет без резинки c окончанием' in f_service else -1
        result['b_deep'] = 1 if 'Глубокий минет c/без резинки' or 'Глубокий минет без резинки c окончанием' or\
                                'Глубокий минет c/без резинки c окончанием' or 'Глубокий минет с резинкой' in f_service else -1
        result['b_ending'] = 1 if '*' in f_service else -1
        result['b_while_driving'] = 1 if '*' in f_service else -1
        result['annilingus'] = 1 if '[!]Анилингус, побалую язычком очко' in f_service else -1
        result['kisses_on_lips'] = 1 if 'Поцелуи в губы' in f_service else -1
        result['kiss_french'] = 1 if 'Французский поцелуй' in f_service else -1
        result['cunnilingus'] = 1 if 'Разрешу куннилингус' in f_service else -1
        result['vaginal_fisting'] = 1 if 'Вагинальный фистинг' in f_service else -1
        result['gangbang'] = 1 if 'Групповуха' in f_service else -1
        result['prof_massage'] = 1 if 'Массаж профессиональный' in f_service else -1
        result['relaxing_massage'] = 1 if 'Расслабляющий массаж' in f_service else -1
        result['classic_massage'] = 1 if 'Классический массаж' in f_service else -1
        result['thai_body_massage'] = 1 if 'Тайский боди массаж' in f_service else -1
        result['erotic_massage'] = 1 if 'Эротический массаж' in f_service else -1
        result['prostate_massage'] = 1 if 'Массаж простаты' in f_service else -1
        result['s_b_massage'] = 1 if 'Ветка сакуры' in f_service else -1
        result['striptease'] = 1 if 'Стриптиз любительский' or 'Стриптиз профессиональный' in f_service else -1
        result['escort'] = 1 if '*' in f_service else -1
        result['video'] = 1 if '*' in f_service else -1
        result['photo'] = 1 if '[!]Сфотографируюется на память' in f_service else -1
        result['phone_sex'] = 1 if 'Секс по телефону' in f_service else -1
        result['serve_couple'] = 1 if 'Услуги семейным парам' in f_service else -1
        result['serve_bachelor'] = 1 if 'Услуги Госпоже' in f_service else -1
        result['role_playing'] = 1 if 'Ролевые игры, наряды' in f_service else -1

        return result


    def get_date(self, max_ancet = 10, start_page = 1, end_page = 1):
        print('Начинаем парсить :)')
        for page_nmb in range(start_page, end_page):
            if self.__open_page_site(page_nmb):
                print('Ошибка открытия сайта!')
                exit(0)
            else:
                soup = BeautifulSoup(self.__browser.page_source, 'html.parser')
                #хрен знает как лучше назвать.... феи они и в Африке феии :)
                feya_prifiles = soup.findAll('div', class_ = 'box profilebox')
                for feya_profile in feya_prifiles:
                    self.feya_profile.append( self.profile_analiysis(feya_profile))
            time.sleep(300)
            print(f'Спарсили страничку № {page_nmb} из {end_page}')
        self.__browser.close()
        self.__browser.quit()


    def saving_data(self, out_format = 'csv'):
        test_date = [{'f_id': '284718', 'date': '2022.10.31', 'is_work': True, 'f_href': 'https://kyz6dar-mibe.xyz/anketa/284718',
          'f_name': 'Лаура', 'phone': '+7(701)024-28-79', 'height': '169см', 'weight': '55кг', 'breasts': '2.5',
          'age': '22', 'nation': 'Казашка', 'city': 'Алматы', 'home_contact': '--', 'home_houer': '20,000 тг',
          'leave_contact': '--', 'leave_houer': '40,000 тг',
          'add_info': 'Казахфильм; ❤️\u200d�Приветствую вас дорогие мужчины); Фото мои 1000%; ❤️\u200d�Делаю профессиональный классический и боди массаж до полного расслабления.; ❤️\u200d�Я не самоучка, обучалась у лучших сенсеев) ес...; ; подробнее; ; ',
          'services': 'Массаж профессиональный; Расслабляющий массаж; Классический массаж; Тайский боди массаж; Массаж простаты; Эротический массаж; Ветка сакуры; ',
          'classic_sex': -1, 'anal_sex': -1, 'b_with_condom': -1, 'b_without_condom': -1, 'b_deep': 1, 'b_ending': -1,
          'b_while_driving': -1, 'annilingus': -1, 'kisses_on_lips': -1, 'kiss_french': -1, 'cunnilingus': -1,
          'vaginal_fisting': -1, 'gangbang': -1, 'prof_massage': 1, 'relaxing_massage': 1, 'classic_massage': 1,
          'thai_body_massage': 1, 'erotic_massage': 1, 'prostate_massage': 1, 's_b_massage': 1, 'striptease': 1,
          'escort': -1, 'video': -1, 'photo': -1, 'phone_sex': -1, 'serve_couple': -1, 'serve_bachelor': -1,
          'role_playing': -1},
         {'f_id': '275588', 'date': '2022.10.31', 'is_work': True, 'f_href': 'https://kyz6dar-mibe.xyz/anketa/275588',
          'f_name': 'Алина спортсменка-', 'phone': '+7(701)024-28-79', 'height': '167см', 'weight': '44кг',
          'breasts': '2.0', 'age': '20', 'nation': 'Азиатка', 'city': 'Алматы', 'home_contact': '--',
          'home_houer': '20,000 тг', 'leave_contact': '--', 'leave_houer': '40,000 тг', 'sauna_contact': '--',
          'sauna_houer': '40,000 тг',
          'add_info': 'Казахфильм; ❤️\u200d�Добрый вечер дорогие мужчины); ⚜️Профессиональная танцовщица и массажистка, обожаю ролевые игры…; Могу быть с подругой; ⚜️Фото 100 %; ⚜️Цены от 15000; ⚜️Хочешь расслабит...; ; подробнее; ; ',
          'services': 'Массаж профессиональный; Расслабляющий массаж; Классический массаж; Тайский боди массаж; Массаж простаты; Эротический массаж; Ветка сакуры; Стриптиз любительский; Поеду отдыхать (в клуб, ресторан и.т.д.). Вечер:300,000 тг; Услуги семейным парам; Услуги Госпоже; Ролевые игры, наряды; Обслуживаю мальчишники. Вечер:300,000 тг; ',
          'classic_sex': -1, 'anal_sex': -1, 'b_with_condom': -1, 'b_without_condom': -1, 'b_deep': 1, 'b_ending': -1,
          'b_while_driving': -1, 'annilingus': -1, 'kisses_on_lips': -1, 'kiss_french': -1, 'cunnilingus': -1,
          'vaginal_fisting': -1, 'gangbang': -1, 'prof_massage': 1, 'relaxing_massage': 1, 'classic_massage': 1,
          'thai_body_massage': 1, 'erotic_massage': 1, 'prostate_massage': 1, 's_b_massage': 1, 'striptease': 1,
          'escort': -1, 'video': -1, 'photo': -1, 'phone_sex': -1, 'serve_couple': 1, 'serve_bachelor': 1,
          'role_playing': 1},
         {'f_id': '58625', 'date': '2022.10.31', 'is_work': True, 'f_href': 'https://kyz6dar-mibe.xyz/anketa/58625',
          'f_name': 'Роза', 'phone': '+7(747)267-31-50', 'height': '165см', 'weight': '50кг', 'breasts': '2.0',
          'age': '25', 'nation': 'Казашка', 'city': 'Алматы', 'home_contact': '20,000 тг', 'home_houer': '35,000 тг',
          'car_contact': '20,000 тг', 'car_houer': '--',
          'add_info': 'Брусиловского; Дорогие мужчины если хотите расслабится и забыть о проблемах на миг то я к вашим услугам прибегу и прилечу на крыльях любви сделаю всё что в моих руках... Работаю у себя... I am speak english... Дор...; ; подробнее; ; ',
          'services': 'Классика; Минет c/без резинки; Анальный секс. Дополнительная плата:40,000 тг; Разрешу куннилингус; [!]Анилингус, побалую язычком очко; Поцелуи в губы; Массаж профессиональный; Расслабляющий массаж; Классический массаж; Массаж простаты; [!]Сделаю минет за рулем. Цена:25,000 тг; Услуги Госпоже; ',
          'classic_sex': 1, 'anal_sex': -1, 'b_with_condom': -1, 'b_without_condom': -1, 'b_deep': 1, 'b_ending': -1,
          'b_while_driving': -1, 'annilingus': 1, 'kisses_on_lips': 1, 'kiss_french': -1, 'cunnilingus': 1,
          'vaginal_fisting': -1, 'gangbang': -1, 'prof_massage': 1, 'relaxing_massage': 1, 'classic_massage': 1,
          'thai_body_massage': -1, 'erotic_massage': -1, 'prostate_massage': 1, 's_b_massage': -1, 'striptease': 1,
          'escort': -1, 'video': -1, 'photo': -1, 'phone_sex': -1, 'serve_couple': -1, 'serve_bachelor': 1,
          'role_playing': -1}]

        columns = [
               'f_id', 'date', 'is_work',
               'f_href', 'f_name', 'phone', 'height', 'age', 'weight', 'nation', 'breasts', 'city', 'home_contact',
               'home_houer', 'leave_contact', 'leave_houer', 'sauna_contact', 'sauna_houer', 'car_contact', 'car_houer',
               'add_info','services', 'height_с', 'weight_с','classic_sex', 'anal_sex', 'b_with_condom', 'b_without_condom', 'b_deep',
               'b_ending', 'b_while_driving', 'annilingus', 'kisses_on_lips', 'kiss_french', 'cunnilingus',
               'vaginal_fisting', 'gangbang', 'prof_massage', 'relaxing_massage', 'classic_massage',
               'thai_body_massage', 'erotic_massage', 'prostate_massage', 's_b_massage', 'striptease', 'escort',
               'video', 'photo', 'phone_sex', 'serve_couple', 'serve_bachelor', 'role_playing'
        ]
        with open(self.FILENAME, "a+", newline="", encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=columns, delimiter=";")
            writer.writeheader()
            writer.writerows(self.feya_profile)