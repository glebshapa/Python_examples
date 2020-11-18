import requests
from bs4 import BeautifulSoup
import csv

HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    'accept': '*/*'}

urls = [
    'https://zipstore.pro/g22561646-zapchasti-dlya-stiralnyh',
    'https://zipstore.pro/g22561648-zapchasti-dlya-holodilnikov',
    'https://zipstore.pro/g22561647-zapchasti-dlya-plit',
    'https://zipstore.pro/g22561649-zapchasti-dlya-vodonagrevatelej',
    'https://zipstore.pro/g22561650-zapchasti-dlya-pylesosov',
    'https://zipstore.pro/g22561651-zapchasti-dlya-myasorubok',
    'https://zipstore.pro/g22561652-zapchasti-dlya-mikrovolnovyh',
    'https://zipstore.pro/g22561620-rashodnye-materialy',
    'https://zipstore.pro/g22561621-instrumenty',
    'https://zipstore.pro/g22561622-konditsionery'
]


def get_html(url, params=None):     # Запрос HTML страницы
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_description(html):              # Парсинг страницы описания
    soup = BeautifulSoup(html, 'html.parser')
    description = soup.find('div', {'data-qaid': 'product_description'}).get_text(strip=True)
    return description


def get_content(html):              # Парсинг HTML страницы
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('li', {'data-qaid': 'product-block'})
    subjects = []
    for item in items:
        subjects.append({
            'title': item.find('a', {'class': 'cs-goods-title'}).get_text(strip=True),
            'arc': item.find('div', {'title': 'Код:'}).find('span').get('title'),
            'price': item.find('span', {'class': 'cs-goods-price__value'}).get_text(strip=True),
            'description': get_description(get_html(item.find('a', {'class': 'cs-goods-title'}).get('href')).text),
        })
    return subjects


def get_pages_count(html):          # Подсчёт страниц определённого товара
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('a', {'class': 'b-pager__link'})
    if pagination:
        return int(pagination[-2].get_text())
    else:
        return 1


def save_file(items, path):         # Сохранение результата в таблицу csv
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Название', 'Артикул', 'Цена', 'Описание'])
        for item in items:
            writer.writerow([item['title'], item['arc'], item['price'], item['description']])


def parse(url, csv_name, dic):                        # Главная функция
    html = get_html(url)
    print(html.status_code)
    subjects = []
    pages_count = get_pages_count(html.text)
    for page in range(1, pages_count + 1):
        html = get_html(url + '/page_' + str(page))
        subjects.extend(get_content(html.text))
    save_file(subjects, f'TOTAL/{dic}/{csv_name}.csv')


def main():
    for url in urls:
        html = get_html(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all('li', {'class': 'cs-product-groups-gallery__item'})
        dic = soup.find('h1', {'class': 'cs-title'}).get_text(strip=True).upper()
        print(dic)
        for item in items:
            file_name = item.find('a', {'class': 'cs-product-groups-gallery__title'}).get_text(strip=True)
            href = 'https://zipstore.pro' + item.find('a', {'class': 'cs-product-groups-gallery__title'}).get('href')
            parse(href, file_name, dic)


main()
