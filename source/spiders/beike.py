__author__ = 'ccinn'
__date__ = '20/8/19 0:20'

# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from scrapy.loader import ItemLoader
from source.sites.beike.beike_item import BeikeItem
from source.utils.strings_utils import extract_schema_domain_from_url, get_nums
import json


class BeikeSpider(scrapy.Spider):
    name = 'beike'
    allowed_domains = ['gz.ke.com']
    start_urls = ['https://gz.ke.com/ershoufang/']
    type = 1
    headers = {
        "HOST": "gz.ke.com",
        "Referer": "https://gz.ke.com",
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/68.0.3440.106 Safari/537.36"
    }

    def parse(self, response):
        '''
        获取总页数开始爬
        :param response:
        :return:
        '''
        # {"totalPage":100,"curPage":1}
        page_data = response.xpath("//div[@comp-module='page']/@page-data").extract_first()
        page_json = json.loads(page_data)
        total_page = page_json['totalPage']
        cur_page = page_json['curPage']
        all_page_urls = [self.start_urls[0]]

        while cur_page <= total_page:
            if cur_page > 1:
                all_page_urls.append(self.start_urls[0] + "pg" + str(cur_page))
            cur_page = cur_page + 1

        # 每页一个协程
        for i, url in enumerate(all_page_urls):
            print("总共 {0} 页, 开始爬取第 {1} 页".format(total_page, i))
            print("*" * 30)
            print("[-] {0} ".format(url))
            print("*" * 30)

            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_page_list)

    def parse_page_list(self, response):
        all_urls = response.xpath("//div[@class='title']/a/@href").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]

        print("{0} 共有 {1} 个房屋信息。".format(response.url, len(all_urls)))

        # 每个详情页一个协程
        for url in all_urls:
            yield scrapy.Request(url, headers=self.headers, callback=self.parse_detail)

    def parse_detail(self, response):
        '''
        解析详情页
        :param response:
        :return:
        '''
        item_loader = ItemLoader(item=BeikeItem(), response=response)
        item_loader.add_value('master_id', get_nums(response.url))  # 108401497579
        item_loader.add_xpath('title', "//div[@class='title']//h1[1]/@title")  # ['康隆苑 大院管理 加装电梯 装修新净']
        item_loader.add_xpath('total_price', "//div[@class='area']//div[1]/text()")  # ['286']
        item_loader.add_xpath('total_area', "//span[@class='total']/text()")  # ['86.07平米']
        item_loader.add_xpath('unit_price_value', "//span[@class='unitPriceValue']/text()")  # ['33228.8']
        item_loader.add_xpath('community_name', "//a[@class='info no_resblock_a']/text()")  # ['康隆苑']
        ## 有一些区域有2个，目前只拿第一个
        item_loader.add_xpath('area', "//div[@class='areaName']/span[@class='info']/a/text()")  # ['海珠']
        item_loader.add_xpath('door_model', "//span[@class='label' and text()='房屋户型']/parent::*/text()")  # ['3室2厅1卫']
        item_loader.add_xpath('has_elevator', "//span[@class='label' and text()='配备电梯']/parent::*/text()")  # ['有']
        item_loader.add_xpath('has_subway',
                              "//div[@class='content']//a[contains(@class,'isNearSubway')]/text()")  # ['\n 地铁 \n']
        item_loader.add_xpath('toward', "//span[@class='label' and text()='房屋朝向']/parent::*/text()")  # ['南']
        item_loader.add_xpath('establish', "//div[@class='area']/div[@class='subInfo']/text()")  # ['1998年建/塔楼']
        item_loader.add_value('spider_src_url', response.url)
        item_loader.add_value('spider_type', self.type)

        # images-pipeline
        item_loader.add_xpath('image_urls', "//div[@data-component='housePhotos']//img/@src")  # ['https://ke-image.ljcdn.com/110000-inspection/pc1_3VySlUq58_1.jpg!m_fill,w_710,h_400,lg_north_west,lx_0,ly_0,l_fbk,f_jpg,ls_50?from=ke.com']

        # 向下抓取小区地址
        addr_url = extract_schema_domain_from_url(response.url) + response.xpath(
            "//a[@class='info no_resblock_a']/@href").extract_first()

        meta = {'item_loader': item_loader}
        yield scrapy.Request(addr_url, headers=self.headers, meta=meta, callback=self.parse_addr)

    def parse_addr(self, response):
        '''
         抓取小区地址
        :param response:
        :return:
        '''
        item_loader = response.meta['item_loader']
        item_loader = ItemLoader(item=item_loader.load_item(), response=response)
        item_loader.add_xpath('addr', "//div[@class='title']/div[@class='sub']/text()")  # ['\n  (海珠)\n   宝业路254号\n  ']
        beike_item = item_loader.load_item()

        yield beike_item

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], dont_filter=True, headers=self.headers)
