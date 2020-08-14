# -*- coding: utf-8 -*-
import scrapy


class BeikeSpider(scrapy.Spider):
    name = 'beike'
    allowed_domains = ['gz.ke.com']
    start_urls = ['https://gz.ke.com/ershoufang/']

    def parse(self, response):
        pass
