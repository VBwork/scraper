from abc import ABC, abstractmethod
import requests
import bs4


class Product:
    def __init__(self, title, price, image):
        self.title = title
        self.price = price
        self.image = image

    def __repr__(self):
        return f'Product: {self.title}'


class ExtendedProduct(Product):
    def __init__(self, title, price, image, brand):
        super().__init__(title, price, image)
        self.brand = brand


class Parser(ABC):
    @abstractmethod
    def start(self):
        pass


class BIParser(Parser):
    url = 'https://bi.ua'

    def get_categories(self):
        response = requests.get(self.url)
        response.raise_for_status()
        category_urls = list()
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        categories = soup.select('ul.navBaseWr a')
        for category in categories[:3]:
            category_url = self.url + category.get('href')
            category_urls.append(category_url)
        return category_urls

    def get_sub_categories(self, category_urls):
        sub_category_urls = list()
        for category_url in category_urls[:3]:
            response = requests.get(category_url)
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            sub_categories = soup.select('div.category a')
            for sub_category in sub_categories[:2]:
                sub_category_url = self.url + sub_category.get('href')
                sub_category_urls.append(sub_category_url)
        return sub_category_urls

    def get_products_urls(self, sub_category_urls):
        product_urls = list()
        for sub_category_url in sub_category_urls[:3]:
            response = requests.get(sub_category_url)
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            products = soup.select('div.catalog a.goodsItemLink')
            for product in products[:3]:
                product_url = self.url + product.get('href')
                product_urls.append(product_url)
        return product_urls

    def get_products(self, product_urls):
        products = list()
        for product_url in product_urls:
            response = requests.get(product_url)
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            title = soup.select_one('h1.h1').text
            price = soup.select_one('p.costIco').text
            image = self.url + soup.select_one('img.prodImg.sourceImgJs').get('src')
            product = Product(title, price, image)
            products.append(product)
        return products

    def start(self):
        category_urls = self.get_categories()
        sub_category_urls = self.get_sub_categories(category_urls)
        product_urls = self.get_products_urls(sub_category_urls)
        products = self.get_products(product_urls)
        print(products)


if __name__ == '__main__':
    BIParser().start()