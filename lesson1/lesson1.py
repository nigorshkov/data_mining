import json
import requests


class Catalogs:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/83.0.4103.116 Safari/537.36",
    }

    def __init__(self, url):
        self.__url = url
        self.__catalog = []
        self.__categories = []

    def parse(self):
        url = self.__url
        response = requests.get(url, headers=self.headers)
        data = response.json()
        self.__categories.extend(data)

        for i in self.__categories:
            self.__catalog = []
            url = 'https://5ka.ru/api/v2/special_offers/'
            while url:
                params = {'categories' : f'{i.get("parent_group_code")}'}
                response = requests.get(url, headers=self.headers, params=params)
                data = response.json()
                url = data['next']
                self.__catalog.extend(data['results'])
                with open(f'{i.get("parent_group_name")}.json', 'w', encoding='UTF-8') as file:
                    json.dump(self.__catalog, file, ensure_ascii=False)


if __name__ == '__main__':
    catalogs = Catalogs('https://5ka.ru/api/v2/categories/')
    catalogs.parse()

