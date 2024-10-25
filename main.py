import re
import json
import requests

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()
metro_store_id = 308
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'User-Agent': ua.random
}
cookies = {
    'metroStoreId': f'{metro_store_id}'
}


def get_product_data(url):
    print(url)
    res = requests.get(url=url, headers=headers, cookies=cookies).text
    soup = BeautifulSoup(res, 'lxml')
    data = {
        'id': None,
        'name': None,
        'url': None,
        'regular_price': None,
        'promo_price': None,
        'brand': None,
    }

    data['id'] = int(re.findall(r'\d+', soup.find('p', class_='product-page-content__article').text)[0])
    data['name'] = soup.find('h1', class_='product-page-content__product-name').find('span').text.strip()
    data['url'] = url
    
    new_price = re.findall(r'\d+\.\d+|\d+', soup.find('div', 'product-unit-prices__actual-wrapper').text.replace('\xa0', ''))
    old_price = re.findall(r'\d+\.\d+|\d+', soup.find('div', 'product-unit-prices__old-wrapper').text.replace('\xa0', ''))
    if old_price:
        data['regular_price'] = float(old_price[0])
        data['promo_price'] = float(new_price[0])
    else:
        data['regular_price'] = float(new_price[0])
        
    for atts in soup.find('ul', class_='product-attributes__list').find_all('li'):
        if 'Бренд' in atts.text:
            data['brand'] = (atts.text.replace('Бренд', '').strip())
            break
    return data


def get_products_links(url):
    links = []
    url = url + '?in_stock=1&order=name_asc'
    res = requests.get(
        url=url,
        headers=headers,
        cookies=cookies
    ).text
    soup = BeautifulSoup(res, 'lxml')
    page_nums = int(soup.find('ul', class_='catalog-paginate v-pagination').find_all('li')[-2].text)
    for i in range(1, page_nums+1):
        res = requests.get(
        url=f'{url}&page={i}',
        headers=headers,
        cookies=cookies
        ).text
        soup = BeautifulSoup(res, 'lxml')
        cards = soup.find_all('div', class_='product-card__content')
        for card in cards:
            links.append(f'https://online.metro-cc.ru{card.find("a", class_="product-card-name")["href"]}')
    return links


def data_to_json():
    links = get_products_links('https://online.metro-cc.ru/category/alkogolnaya-produkciya/pivo-sidr/pivo-svetloe')
    data = [get_product_data(link) for link in links]
    with open(f'store{metro_store_id}_data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    data_to_json()


if __name__ == '__main__':
    main()
