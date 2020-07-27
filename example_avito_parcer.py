import requests
from bs4 import BeautifulSoup
import csv

URL = 'https://www.avito.ru/nizhniy_novgorod/fototehnika/obektivy-ASgBAgICAUS~A6YX?cd=1'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    'accept': '*/*'}
HOST = 'https://www.avito.ru/'
FILE = 'subjects.csv'


def get_html(url, params=None):     # Запрос HTML страницы
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_pages_count(html):          # Подсчёт страниц определённого товара
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', {'class': 'pagination-item-1WyVp'})
    if pagination:
        return int(pagination[-2].get_text())
    else:
        return 1


def get_content(html):              # Парсинг HTML страницы
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', {'class': 'item_table'})
    subjects = []
    for item in items:
        subjects.append({
            'title': item.find('span', {'itemprop': 'name'}).get_text(strip=True),
            'link': HOST + item.find('a', {'class': 'snippet-link'}).get('href'),
            'price': item.find('meta', {'itemprop': 'price'}).get('content') + ' rub'
        })
    return subjects


def save_file(items, path):         # Сохранение результата в таблицу csv
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Название', 'Ссылка', 'Цена'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['price']])


def parse():                        # Главная функция
    html = get_html(URL)
    if html.status_code == 200:
        subjects = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Parcing page {page} / {pages_count}')
            html = get_html(URL, params={'p': page})
            subjects.extend(get_content(html.text))
        save_file(subjects, FILE)
        print(f'Total: {len(subjects)} subject/s')
    else:
        print('Error')


parse()
