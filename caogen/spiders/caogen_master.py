# -*- coding: utf-8 -*-
import scrapy
from caogen.model.config import REDIS_CONN


class CaogenMasterSpider(scrapy.Spider):
    name = 'caogen_master'
    allowed_domains = ['caogen.com']
    base_url = "http://www.caogen.com/infor_more/1/%d.html"
    current_page = 1
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0"}

    def __init__(self, name=None, **kwargs):
        # 实例化redis
        self.redis_conn = REDIS_CONN
        super(CaogenMasterSpider, self).__init__(name, **kwargs)

    def start_requests(self):
        start_url = self.base_url % self.current_page
        yield scrapy.Request(url=start_url, headers=self.headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        links = response.xpath('//td/a[@class="fontsize14"]/@href').extract()
        # 这里只爬文章url就简单的判断一下
        for link in links:
            if not 'ID' in link:
                master_url = "http://www.caogen.com" + link
                # 将获取的链接送入redis
                self.send_to_redis(value=master_url)

    def send_to_redis(self, key='master:requests', value=None):
        """
        将request请求放进redis
        :param key:默认master服务器
        :param value:url以及一些别的附带的信息
        :return:
        """
        print value
        print type(value)
        self.redis_conn.sadd(key, value)
        print "Success send to Redis!"
