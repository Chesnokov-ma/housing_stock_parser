import requests
from bs4 import BeautifulSoup
import json
import csv
import openpyxl
import time
import os
import pandas as pd
start_time = time.time()

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

    def get_all_pages(self, soup):
        pagination = soup.find(class_='pagination').find_all('li')
        page_a = pagination[-1].find('a')
        last_page = page_a.get('data-ci-pagination-page')
        all_pages = int(last_page)

        all_pages_dictionary = {}
        for num_page in range(1, all_pages + 1):
            num_page_str = str(num_page)
            num_page_href = 'https://dom.mingkh.ru/primorskiy-kray/vladivostok/?page=' + num_page_str
            num_page_text = 'Page №' + num_page_str
            all_pages_dictionary[num_page_text] = num_page_href
        return all_pages_dictionary

    def get_data(self, all_pages_dict):
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
            if (page_count == 1): break

        with open(f"data.json", "a", encoding="cp1251") as file:
            json.dump(houses_info, file, indent=4, ensure_ascii=False)

        os.remove('data.html')
        os.remove('data_page.html')
        return 0


# stock = Data_capture()
# req = stock.get_request("https://dom.mingkh.ru/primorskiy-kray/vladivostok/")
# r_src = req.text
# src = stock.get_html(r_src)
# soup = BeautifulSoup(src, "lxml")
# all_pages_dict = stock.get_all_pages(soup)
# stock.get_data(all_pages_dict)

def read_data(file_name):
    csv_data = pd.read_csv(file_name, delimiter=';')
    housing_data = pd.DataFrame(csv_data)
    # print(housing_data)
    # print(housing_data.columns)
    # housing_data = housing_data.sort_values(by = 'Год постройки', ascending = False)
    # print(housing_data[['Адрес', 'Год постройки']])
    return housing_data

data_hsp = read_data('data.csv')
print(data_hsp)

end_time = time.time() - start_time
end_time = round(end_time, 3)
print(f'Total running time of the program: {end_time} sec')