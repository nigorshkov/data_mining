from bs4 import BeautifulSoup as bs
import requests
import json
from pymongo import MongoClient


class GbBlogParse:
    __domain = 'https://geekbrains.ru'
    __url = 'https://geekbrains.ru/posts'
    __done_urls = set()

    def __init__(self):
        client = MongoClient('mongodb://localhost:27017')
        database = client['parse_geekbrains']
        self.collection = database['articles']
        self.posts_urls = set()
        self.pagination_urls = set()
        self.articles = list()

    def get_page_soap(self, url):
        # todo метод запроса страницы и создания супа
        response = requests.get(url)
        soup = bs(response.text, 'lxml')
        return soup

    def run(self, url=None):
        # todo метод запуска парсинга
        url = url or self.__url
        soup = self.get_page_soap(url)
        self.pagination_urls.update(self.get_pagination(soup))

        for url in tuple(self.pagination_urls):
            if url not in self.__done_urls:
                self.__done_urls.add(url)
                self.posts_urls.update(self.get_posts_urls(soup))
                self.run(url)


    # todo Проход пагинации ленты
    def get_pagination(self, soup):
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        a_list = [f'{self.__domain}{a.get("href")}' for a in ul.find_all('a') if a.get("href")]
        return a_list

    # todo Поиск ссылок на статьи на странице ленты
    def get_posts_urls(self, soup):
        posts_wrap = soup.find('div', attrs={'class': 'post-items-wrapper'})
        a_list = [f'{self.__domain}{a.get("href")}' for a in
                  posts_wrap.find_all('a', attrs={'class': 'post-item__title'})]

        return a_list

    # todo Поиск информации на странице статьи
    def get_article(self):
        info = []
        for i in self.posts_urls:
            article_info = {}
            response = requests.get(i)
            soup = bs(response.text, 'lxml')
            article_info['title'] = soup.find('h1', attrs={'class': 'blogpost-title'}).contents[0]
            article_info['post_url'] = i
            article_info['writer_name'] = soup.find('div', attrs={'class': 'text-lg'}).contents[0]
            article_info['writer_url'] = f"{self.__domain}{soup.find('div', attrs={'class': 'col-md-5'}).find('a').get('href')}"
            tags_urls = []
            for j in soup.find_all('a', attrs={'class': 'small'}):
                tags_urls.append(j.contents[0])
            article_info['tags_urls'] = tags_urls
            images = []
            img_all = soup.find('div', attrs={'class': ['blogpost-content']}).find_all('img')
            for j in range(0, len(img_all)):
                images.append(img_all[j].get('src'))
            article_info['images'] = images
            article_info['text'] = soup.find('div', attrs={'class': ['blogpost-content']}).text
            info.append(article_info)
        self.articles = info

    #todo Сохраяем в файл
    def save_to_file(self):
        with open(f'posts.json', 'w', encoding='UTF-8') as file:
            json.dump(self.articles, file, ensure_ascii=False)

    #todo Сохраняем в Mongo
    def save_to_mongo(self):
        self.collection.insert_many(self.articles)


if __name__ == '__main__':
    parser = GbBlogParse()
    parser.run()
    parser.get_article()
    parser.save_to_mongo()
