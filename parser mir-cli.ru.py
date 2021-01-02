import requests
from bs4 import BeautifulSoup

from datetime import datetime
import json
from multiprocessing import Pool


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36', 'accept': '*/*'}
HOST = 'https://mircli.ru'
j = 0


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)

    return r.text  # возвращает html код страницы (url)


def get_pages_count(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        pagination = soup.find_all('ul', class_='pagination')[
            2].find('a').get('href').split('=')[1]
        print(pagination)
    except:
        pagination = 0
    if pagination:
        return int(pagination)
    else:
        return 1


def get_all_links(html):
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find(
        'section', id='section-products').find_all('div', class_='product-content')

    links = []

    for div in divs:
        a = HOST + div.find('a', class_='prod_a').get('href')

        links.append(a)

    return (links)


def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        cats = soup.find(
            'ul', class_='main-menu-breadcrumbs').find_all('span', itemprop='name')
    except:
        cats = ''
    try:
        atrs = soup.find(
            'div', id='product-overview-2').find_all('span', class_='main')
    except:
        atrs = ''
    try:
        img = HOST + \
            soup.find('div', id='fotorama-product').find_next('img').get('src')
    except:
        img = ''
    try:
        product_prefix = soup.find('h1', itemprop='name').find_next(
            'span', class_='product-prefix').text.strip()
        product_name = soup.find('h1', itemprop='name').find_next(
            'span', class_='product-name').text.strip()
        name = product_prefix + ' ' + product_name

    except:
        name = ''
    try:
        opis = soup.find('div', class_='show-more-block-new').text.strip()

    except:
        opis = ''

    try:
        price = soup.find(
            'div', class_='block-price').find_next('span', class_='price').text.strip(' руб')
    except:
        price = ''

    try:
        article = soup.find('span', class_='vendor-code').text.strip()
    except:
        article = ''

    print(article, img)

    data = {
        'название': name,
        'Артикул': article,
        'Цена': price.replace(' ', ''),
        'Картинка': img,
        'Описание': opis,
    }
    i = 0
    for cat in cats:
        i = i + 1
        cat_num = 'Категория ' + str(i)
        cat_name = cat.text.strip()
        data[cat_num] = cat_name

    for atr in atrs:

        atr_name = atr.text.strip().replace('  ', '').replace('?', '').replace('\n', '')
        atr_value = atr.find_next('span', class_='page').text.strip()
        data[atr_name] = atr_value

    return data


def write_csv(data_dict):
    try:
        json_data = json.load(open('persons.json'))
    except:
        json_data = []

    json_data.append(data_dict)

    with open('persons.json', 'a', encoding='utf-8') as file:
        json.dump(json_data, file, indent=2, ensure_ascii=False)

        print(data_dict['название'], data_dict['Цена'], 'parsed')


def make_all(url):
    html = get_html(url)
    data = get_page_data(html)
    write_csv(data)


def main():

    start = datetime.now()

    urls = ['https://mircli.ru/uvlazhniteli-vozduha/',
            'https://mircli.ru/mojki-vozduha/'
            ]
    for url in urls:

        pages_count = get_pages_count(get_html(url))
        for pages in range(1, pages_count + 1):
            print(pages, 'из', pages_count)
            # передает адреса страниц с параметрами номеров
            all_links = get_all_links(get_html(url, params={'page': pages}))

            with Pool(1) as p:
                p.map(make_all, all_links)

    # for url in all_links:
    #    html = get_html(url)
    #    data = get_page_data(html)
    #    write_csv(data)

    end = datetime.now()
    total = end-start

    print(str(total))
    print(pages_count)


if __name__ == '__main__':
    main()
