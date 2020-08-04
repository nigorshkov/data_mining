import scrapy
import re
import json
from copy import deepcopy
from inst.items import InstItem
from scrapy.loader import ItemLoader

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __api_url = '/graphql/query/'
    __api_query = {
        'posts_feed': '7437567ae0de0773fd96545592359a6b',
    }
    variables = {"id": "", "first": 12, "after": ""}

    def __init__(self, login, passwd, parse_users: list, *args, **kwargs):
        self.login = login
        self.passwd = passwd
        self.parse_users = parse_users
        super().__init__(*args, **kwargs)

    def parse(self, response):
        token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.__login_url,
            method='POST',
            callback=self.im_login,
            formdata={
                'username': self.login,
                'enc_password': self.passwd,
            },
            headers={'X-CSRFToken': token}
        )

    def im_login(self, response):
        data = response.json()
        if data['authenticated']:
            for user_name in self.parse_users:
                yield response.follow(f'/{user_name}',
                                      callback=self.user_parse,
                                      cb_kwargs={'user_name': user_name})

    def user_parse(self, response, user_name):
        # немного костыльно надо подумать над упрощением
        user_id = self.fetch_user_id(response.text, user_name)
        variables = deepcopy(self.variables)
        variables['id'] = f"{user_id}"
        url = f"{self.__api_url}?query_hash={self.__api_query['posts_feed']}&variables={json.dumps(variables)}"
        yield response.follow(url, callback=self.user_feed_parse, cb_kwargs={'user_name': user_name,
                                                                             'variables': variables})

    def user_feed_parse(self, response, user_name, variables):
        data = response.json()
        for itm in data['data']['user']['edge_owner_to_timeline_media']['edges']:
            item = ItemLoader(InstItem(), itm)
            item.add_value('user_name', user_name)
            item.add_value('user_id', variables['id'])
            photos = []
            if 'edge_sidecar_to_children' in itm['node']:
                for photo in itm['node']['edge_sidecar_to_children']['edges']:
                    photos.append(photo['node']['display_url'])
            else:
                photos.append(itm['node']['display_url'])
            item.add_value('post_photos', photos)
            item.add_value('post_pub_date', itm['node']['taken_at_timestamp'])
            item.add_value('like_count', itm['node']['edge_media_preview_like']['count'])
            yield item.load_item()

        page_info = data['data']['user']['edge_owner_to_timeline_media']['page_info']
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']
            url = f"{self.__api_url}?query_hash={self.__api_query['posts_feed']}&variables={json.dumps(variables)}"
            yield response.follow(url, callback=self.user_feed_parse, cb_kwargs={'user_name': user_name,
                                                                                 'variables': variables})

    def fetch_user_id(self, text, username):
        """Используя регулярные выражения парсит переданную строку на наличие
        `id` нужного пользователя и возвращет его."""
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def fetch_csrf_token(self, text):
        """Используя регулярные выражения парсит переданную строку на наличие
        `csrf_token` и возвращет его."""
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')
