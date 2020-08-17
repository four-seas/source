# -*- coding: utf-8 -*-
import scrapy
from urllib import parse

class BeikeSpider(scrapy.Spider):
    name = 'beike'
    allowed_domains = ['gz.ke.com']
    start_urls = ['https://gz.ke.com/ershoufang/']

    headers = {
        "HOST": "gz.ke.com",
        "Referer": "https://gz.ke.com",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/68.0.3440.106 Safari/537.36"
    }

    def parse(self, response):
        # print(response.css('div[class=title]::attr(href)').extract())
        # print(response.css('a[class*=maidian-detail]::attr(href)').extract())
        # print(response.xpath("//div[@class='title']/a/text()").extract())
        # self.log('A response from %s just arrived!' % response.url)
        # print(response)
        # self.log('%s' % response.text)

        all_urls = response.xpath("//div[@class='title']/a/@href").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]

        for url in all_urls:
            yield scrapy.Request(url, headers=self.headers, callback=self.parse_content)

    def parse_content(self, response):
        # print(response.xpath("//div[@class='title']/a/text()").extract())
        # print(response.xpath('//div[@class="positionInfo"]/a/@href').extract())
        print(response.xpath("//a[@class='info no_resblock_a']/text()").extract())

    def start_requests(self):
        max_page = 100
        page = 2
        while page < max_page:
            self.start_urls.append(self.start_urls[0] + "pg" + str(page) + "/")
            page = page + 1

        for url in self.start_urls:
            yield scrapy.Request(url=url, dont_filter=True, headers=self.headers)
