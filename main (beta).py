import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import os
import pandas as pd
from collections import Counter
import numpy
import matplotlib.pyplot as plt
import seaborn as sns

class Data_capture:

    def __init__(self):
        pass

    def get_request(self, url):
        headers = {
            "Accept": "*/*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 YaBrowser/23.3.4.603 Yowser/2.5 Safari/537.36"
        }
        req = requests.get(url, headers=headers)
        return req

    def get_html(self, r_src):
        with open("data.html", "w", encoding='utf-8') as file:
            file.write(r_src)

        with open("data.html", encoding='utf-8') as file:
            src = file.read()
        return src

    def get_all_pages(self, soup, s_url):
        pagination = soup.find(class_='pagination').find_all('li')
        page_a = pagination[-1].find('a')
        last_page = page_a.get('data-ci-pagination-page')
        all_pages = int(last_page)

        all_pages_dictionary = {}
        for num_page in range(1, all_pages + 1):
            num_page_str = str(num_page)
            num_page_href = 'https://dom.mingkh.ru' + s_url + '?page=' + num_page_str
            num_page_text = 'Page №' + num_page_str
            all_pages_dictionary[num_page_text] = num_page_href
        return all_pages_dictionary

    def get_data(self, all_pages_dict, web_pages):
        with open('all_pages.json', 'w') as file:
            json.dump(all_pages_dict, file, indent=4, ensure_ascii=False)

        with open('all_pages.json') as file:
            all_pages = json.load(file)

        # Сбор заголовков таблицы
        address = 'Адрес'
        year_of_construction = 'Год постройки'
        number_of_floors = 'Количество этажей'
        house_type = 'Тип дома'
        living_quarters = 'Жилых помещений'
        building_type = 'Серия, тип постройки'
        floor_type = 'Тип перекрытий'
        load_bearing_wall_material = 'Материал несущих стен'
        disrepair = 'Признан аварийным'

        with open(f'data.csv', 'w') as file:
            file.close()
        with open(f'data.json', 'w') as file:
            file.close()

        with open(f"data.csv", "a", encoding="utf-8-sig", newline='') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(
                [address, year_of_construction, number_of_floors, house_type, living_quarters, building_type, floor_type,
                 load_bearing_wall_material, disrepair])

        page_count = 0

        for num_page, page_href in all_pages.items():
            print(num_page)
            req = self.get_request(page_href)
            src = req.text
            with open('data_page.html', "w", encoding='utf-8') as file:
                file.write(src)

            with open('data_page.html', encoding='utf-8') as file:
                src = file.read()

            soup = BeautifulSoup(src, "lxml")
            addresses_table = soup.find(class_='table table-condensed table-hover table-striped').find('tbody').find_all(
                'tr')
            houses_info = []

            for item in addresses_table:
                address_href = item.find('a')
                address_href = address_href.get('href')
                # print(address_href)
                req_address = self.get_request('https://dom.mingkh.ru' + address_href)
                src_address = req_address.text
                # print(src_address)
                soup = BeautifulSoup(src_address, 'lxml')
                house_head_table = soup.find(class_='dl-horizontal house').find_all('dt')
                house_info_table = soup.find(class_='dl-horizontal house').find_all('dd')

                head_info = {}
                for i, j in zip(house_head_table, house_info_table):
                    head_info[i.text] = j.text

                # Сбор данных таблицы
                if 'Адрес' in head_info.keys():
                    address = head_info['Адрес']
                    address = address.replace('\xa0\xa0\xa0На карте', '')
                else:
                    address = 'Нет данных'

                if 'Год постройки' in head_info.keys():
                    year_of_construction = head_info['Год постройки']
                else:
                    year_of_construction = 'Нет данных'

                if 'Количество этажей' in head_info.keys():
                    number_of_floors = head_info['Количество этажей']
                    number_of_floors = number_of_floors.replace(' ', '')
                else:
                    number_of_floors = 'Нет данных'

                if 'Тип дома' in head_info.keys():
                    house_type = head_info['Тип дома']
                else:
                    house_type = 'Нет данных'

                if 'Жилых помещений' in head_info.keys():
                    living_quarters = head_info['Жилых помещений']
                else:
                    living_quarters = 'Нет данных'

                if 'Серия, тип постройки' in head_info.keys():
                    building_type = head_info['Серия, тип постройки']
                else:
                    building_type = 'Нет данных'

                if 'Тип перекрытий' in head_info.keys():
                    floor_type = head_info['Тип перекрытий']
                else:
                    floor_type = 'Нет данных'

                if 'Материал несущих стен' in head_info.keys():
                    load_bearing_wall_material = head_info['Материал несущих стен']
                else:
                    load_bearing_wall_material = 'Нет данных'

                if 'Дом признан аварийным' in head_info.keys():
                    disrepair = head_info['Дом признан аварийным']
                else:
                    disrepair = 'Нет данных'

                houses_info.append(
                    {
                        'Address': address,
                        'Year of construction': year_of_construction,
                        'Number of floors': number_of_floors,
                        'House type': house_type,
                        'Living quarters': living_quarters,
                        'Building type': building_type,
                        'Floor type': floor_type,
                        'Load-bearing wall material': load_bearing_wall_material,
                        'Disrepair': disrepair
                    }
                )
                print(address)
                with open(f"data.csv", "a", encoding="utf-8-sig", newline='') as file:
                    writer = csv.writer(file, delimiter=";")
                    writer.writerow(
                        [address, year_of_construction, number_of_floors, house_type, living_quarters, building_type,
                         floor_type, load_bearing_wall_material, disrepair]
                    )

            page_count += 1
            if (page_count == web_pages): break

        with open(f"data.json", "a", encoding="cp1251") as file:
            json.dump(houses_info, file, indent=4, ensure_ascii=False)

        os.remove('data.html')
        os.remove('data_page.html')
        return 0

class Read_stock:
    def __init__(self):
        pass

    def read_data(self, file_name):
        csv_data = pd.read_csv(file_name, delimiter=';')
        housing_data = pd.DataFrame(csv_data)
        return housing_data

class Graphs:
    def __init__(self):
        pass

    def bar_chart_hsp(self, data_hsp_column, discription, name_c):
        data_hsp_list = data_hsp_column.tolist()
        data_array_counts = dict(Counter(data_hsp_list))

        if 'Нет данных' in data_array_counts.keys():
            del data_array_counts['Нет данных']

        df = pd.DataFrame(data_array_counts.items(), columns = ['key', 'val'])
        df = df.sort_values(by = 'val', ascending = True)

        fig, ax = plt.subplots(figsize = (8,8))
        bars = plt.barh(df['key'], df['val'], color = '#4f65ad')
        ax.bar_label(bars, color = 'black', fontsize = 10, label_type = 'edge', fontweight = 'bold')
        ax.set_title('Диаграмма распределения домов (г. '+ name_c+')')
        ax.set_ylabel(discription)
        plt.show()

        return 0

    def pie_diagram_hsp(self, data_hsp_column, discription, name_c):
        data_hsp_list = data_hsp_column.tolist()
        data_array_counts = dict(Counter(data_hsp_list))

        df = pd.DataFrame(data_array_counts.items(), columns=['key', 'val'])
        df = df.sort_values(by='val', ascending=True)

        sns.set(font_scale = 1)
        plt.figure(figsize=(8, 8))

        plt.pie(df['val'], labels=df['key'], autopct='%.1f%%', colors = sns.color_palette('Set2'), startangle=90)
        plt.title(discription + ' (г. '+ name_c + ')')
        plt.show()

        return 0

class Summon_operations:
    def __init__(self):
        pass
    def data_capture_op(self, city_url):
        start_time = time.time()

        stock = Data_capture()
        req = stock.get_request('https://dom.mingkh.ru' + city_url)
        r_src = req.text
        src = stock.get_html(r_src)
        soup = BeautifulSoup(src, "lxml")
        all_pages_dict = stock.get_all_pages(soup, city_url)
        stock.get_data(all_pages_dict, 4)

        end_time = time.time() - start_time
        end_time = round(end_time, 3)
        print(f'\nTotal running time of scraping: {end_time} sec\n')

        return 0
    def graphs_op(self, num_op_2, c_name):

        num_operation_dict_2 = {'1': '"Год постройки"',
                                '2': '"Количество этажей"',
                                '3': '"Тип дома"',
                                '4': '"Количество жилых помещений"',
                                '5': '"Тип перекрытий"',
                                '6': '"Материал несущих стен"',
                                '7': '"Признан аварийным"'}

        data_file = Read_stock()
        data_hsp = data_file.read_data('data.csv')

        data_hsp = data_hsp.astype(str)
        data_graph = Graphs()

        if (num_op_2 == '1'):
            print(f'Диаграмма по параметру: {num_operation_dict_2[num_op_2]}\n')
            data_graph.bar_chart_hsp(data_hsp['Год постройки'], 'Год постройки',
                                     c_name)  # вызов метода столбчатой диаграммы по году постройки домов
        elif (num_op_2 == '2'):
            print(f'Диаграмма по параметру: {num_operation_dict_2[num_op_2]}\n')
            data_graph.bar_chart_hsp(data_hsp['Количество этажей'], 'Количество этажей',
                                     c_name)  # вызов метода столбчатой диаграммы по числу этажей
        elif (num_op_2 == '3'):
            print(f'Диаграмма по параметру: {num_operation_dict_2[num_op_2]}\n')
            data_graph.pie_diagram_hsp(data_hsp['Тип дома'], 'Тип дома', c_name)  # вызов метода круговой диаграммы
        elif (num_op_2 == '4'):
            print(f'Диаграмма по параметру: {num_operation_dict_2[num_op_2]}\n')
            data_graph.bar_chart_hsp(data_hsp['Жилых помещений'], 'Количество жилых помещений',
                                     c_name)  # вызов метода столбчатой диаграммы по числу жилых
        elif (num_op_2 == '5'):
            print(f'Диаграмма по параметру: {num_operation_dict_2[num_op_2]}\n')
            data_graph.pie_diagram_hsp(data_hsp['Тип перекрытий'], 'Тип перекрытий',
                                       c_name)  # вызов метода круговой диаграммы
        elif (num_op_2 == '6'):
            print(f'Диаграмма по параметру: {num_operation_dict_2[num_op_2]}\n')
            data_graph.pie_diagram_hsp(data_hsp['Материал несущих стен'], 'Материал несущих стен',
                                       c_name)  # вызов метода круговой диаграммы
        elif (num_op_2 == '7'):
            print(f'Диаграмма по параметру: {num_operation_dict_2[num_op_2]}\n')
            data_graph.pie_diagram_hsp(data_hsp['Признан аварийным'], 'Признан аварийным',
                                       c_name)  # вызов метода круговой диаграммы
        elif (num_op_2 == '0'):
            print('\n')
            pass
        else:
            print('НЕВЕРНО ВВЕДЁН НОМЕР ОПЕРАЦИИ!\n')
        return 0
    def replace_city_op(self, city_dict, curr_c_url):
        current_city_name = dict_key_read(city_dict, curr_c_url)
        print(f'Текущий город - {current_city_name}\n')

        tmd = False
        while (tmd == False):
            replace_city_name = input('г. Москва\n'
                                      'г. Санкт-Петербург\n'
                                      'г. Казань\n'
                                      'г. Владивосток\n'
                                      '0) Назад\n\n'
                                      'Введите название города для сбора данных по его жилищному фонду: ')

            if replace_city_name == '0':
                tmd = True
            elif replace_city_name in city_dict:
                tmd = True
                curr_c_url = city_dict[replace_city_name]
                print(f'Город {current_city_name} сменён на город {replace_city_name}\n')
            else:
                print('ГОРОД НЕ НАЙДЕН!\n')

        return curr_c_url

def dict_key_read(cd, ccu):
    for k, v in cd.items():
        if v == ccu:
            dict_key = k
    return dict_key


summon = Summon_operations()

cities = {'Москва': '/moskva/moskva/',
          'Санкт-Петербург': '/sankt-peterburg/sankt-peterburg/',
          'Казань': '/tatarstan/kazan/',
          'Владивосток': '/primorskiy-kray/vladivostok/'}

current_city_url = cities['Владивосток']

num_operation_dict = {'0': 'Завершение работы',
                      '1': 'Сбор данных',
                      '2': 'Построение диаграммы',
                      '3': 'Изменение города'}

num_operation = '1'
while(num_operation != '0'):
    num_operation = input('1) Выполнить сбор данных\n'
                          '2) Построить диаграмму\n'
                          '3) Сменить город\n'
                          '0) Закрыть программу\n\n'
                          'Выберите операцию и введите её номер: ')

    if (num_operation == '1'):
        print(f'{num_operation_dict[num_operation]}\n')
        summon.data_capture_op(current_city_url)

    elif (num_operation == '2'):
        print(f'{num_operation_dict[num_operation]}\n')

        num_operation_2 = '1'
        while(num_operation_2 != '0'):
            num_operation_2 = input('1) "Год постройки"\n'
                                    '2) "Количество этажей"\n'
                                    '3) "Тип дома"\n'
                                    '4) "Количество жилых помещений"\n'
                                    '5) "Тип перекрытий"\n'
                                    '6) "Материал несущих стен"\n'
                                    '7) "Признан аварийным"\n'
                                    '0) Назад\n\n'
                                    'Выберите параметр данных, по которому нужно построить диаграмму, и введите его номер: ')
            city_name = dict_key_read(cities, current_city_url)
            print(city_name)
            summon.graphs_op(num_operation_2, city_name)

    elif (num_operation == '3'):

        print(f'{num_operation_dict[num_operation]}\n')
        current_city_url = summon.replace_city_op(cities, current_city_url)

    elif (num_operation == '0'):
        print(f'{num_operation_dict[num_operation]}\n')

    else:
        print('НЕВЕРНО ВЫБРАНА ОПЕРАЦИЯ!\n')