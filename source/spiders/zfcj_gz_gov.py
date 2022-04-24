__author__ = 'ccinn'
__date__ = '22/04/21 14:49'

# -*- coding: utf-8 -*-
import urllib

import scrapy
from urllib import parse
from scrapy.loader import ItemLoader
from source.sites.gov.gov_item import GovProjectItem
from source.sites.gov.gov_mc_item import GovMcItem
import json


class ZfcjGzGovSpider(scrapy.Spider):
    name = 'zfcj_gz_gov'
    allowed_domains = ['zfcj.gz.gov.cn']
    # start_urls = ['http://zfcj.gz.gov.cn/zfcj/fyxx/xmxkbxxView']
    start_urls = ['http://zfcj.gz.gov.cn/zfcj/fyxx/xmxkbxxList']
    headers = {
        "HOST": "zfcj.gz.gov.cn",
        "Referer": "http://zfcj.gz.gov.cn/zfcj/fyxx/xkb?sProjectId=100000023707&sPreSellNo=20210946",
        'Origin': 'http://zfcj.gz.gov.cn',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/68.0.3440.106 Safari/537.36"
    }

    def parse(self, response: scrapy.http.Response):
        # print(response.body)
        # ['房号', '类型', '总面积（平方米）', '户型', '状态', '抵押', '查封']
        m = {
            'unit_number': 0,
            'unit_type': 1,
            'unit_total_area': 2,
            'unit_house_type': 3,
            'status': 4,
            'charge': 5,
            'attachment': 6
        }
        # print(response.xpath('//table//th//text()').getall())
        n = len(response.xpath('//table//th//text()').getall())
        # 数据
        item_list = response.xpath('//table//td//text()').getall()
        # print(response.xpath('//table//td//text()').getall())
        item_list = [item_list[i:i + n] for i in range(0, len(item_list), n)]
        for item in item_list:
            item_loader = ItemLoader(item=GovMcItem())
            for key in m:
                if key in m.keys():
                    item_loader.add_value(key, item[m[key]])
            it = item_loader.load_item()
            yield it

        # item_loader.add_value('master_id', get_nums(response.url))  # 108401497579
        # item_loader.add_xpath('title', "//div[@class='title']//h1[1]/@title")  # ['康隆苑 大院管理 加装电梯 装修新净']
        # item_loader.add_xpath('total_price', "//div[@class='area']//div[1]/text()")  # ['286']
        # item_loader.add_xpath('total_area', "//span[@class='total']/text()")  # ['86.07平米']
        # item_loader.add_xpath('unit_price_value', "//span[@class='unitPriceValue']/text()")  # ['33228.8']
        # item_loader.add_xpath('community_name', "//a[@class='info no_resblock_a']/text()")  # ['康隆苑']
        # ## 有一些区域有2个，目前只拿第一个
        # item_loader.add_xpath('area', "//div[@class='areaName']/span[@class='info']/a/text()")  # ['海珠']
        # item_loader.add_xpath('door_model', "//span[@class='label' and text()='房屋户型']/parent::*/text()")  # ['3室2厅1卫']
        # item_loader.add_xpath('has_elevator', "//span[@class='label' and text()='配备电梯']/parent::*/text()")  # ['有']
        # item_loader.add_xpath('has_subway',
        #                       "//div[@class='content']//a[contains(@class,'isNearSubway')]/text()")  # ['\n 地铁 \n']
        # item_loader.add_xpath('toward', "//span[@class='label' and text()='房屋朝向']/parent::*/text()")  # ['南']
        # item_loader.add_xpath('establish', "//div[@class='area']/div[@class='subInfo']/text()")  # ['1998年建/塔楼']
        # item_loader.add_value('spider_src_url', response.url)
        # item_loader.add_value('spider_type', self.type)
        #
        # # images-pipeline
        # item_loader.add_xpath('image_urls',
        #                       "//div[@data-component='housePhotos']//img/@src")  # ['https://ke-image.ljcdn.com/110000-inspection/pc1_3VySlUq58_1.jpg!m_fill,w_710,h_400,lg_north_west,lx_0,ly_0,l_fbk,f_jpg,ls_50?from=ke.com']
        #
        # # 向下抓取小区地址
        # addr_url = extract_schema_domain_from_url(response.url) + response.xpath(
        #     "//a[@class='info no_resblock_a']/@href").extract_first()
        #
        # meta = {'item_loader': item_loader}
        # yield scrapy.Request(addr_url, headers=self.headers, meta=meta, callback=self.parse_addr)

    def start_requests(self):
        body = {
            'sProjectId': 100000023707,
            'token': 'eE3o8ECLLfa/83oI2T2rE1J4uKavcNQo6ME5tKXH/uSKwIRzCMqoGLwTV5O16stgIb9WOWOI5LTrBGz+whfQ5OZSJVzxQzPlPxbEGGZk/+bF4ZNPpTvyDGaV14eI8iPH5j7sgBR8R9aibk9XpqrrwwbSKSyxCG75U/r1HXQfrSs=@czNTyYoYf+K3odgNezsMmxP/81Enp4dJN+vrkdQ+wlkC8gXe0hZisTxgmEkHDs+ebEh19Ol6w5DkftTzGrzfcZ0p7/q4Mb977bJe8yv340P5KDHDLzVjavO7do5q8sw/e/3HxJSDjhGdXx2NV3yaB8oj8Di4/wlsSaNUy4WCIU4=@fXsS/cWL4M15HjFTcS7jFbrbw5EfISR0MyPLFUyw9BcRo9GvgrfDLrLrvYpO+97cq2+dSsGWArlZGbU7luHKq/l8NKgFB2Fs7FKkN8XhlrWxcFcZExPj+cv76cJUMel7sbwnoEjoFJio8KmH9Ca+EJ707N2uSNy84XRkhmElZjQ=@gPJ0g+BSkoxck/+HKfDuZbpOtDBr8XnS5bWTdm6sxj0sjqO6yqlOn5xEuNveBzpV6wkgp7fQ21Qj64vlM6YogKX5Kc7mc14zr3a2o1e0lgb8ODcrJTpYvoxxIXU/XSeq7n8KCh9oschi4Sn2dqEcN7zsRFCmkZkdvc/mtAILZJ4=@eIKLGKqxe/b7C1HJWsDgtWKe7Ukhfc02IEsZ3z8HV9boIJ8TNuDwSfGfKUdJvxw+ZiZBSUn/gTPtbja9CsfEjkYdAiAhGPFswyJ4p2Itk+AGPY8R7uagu4qjunKjPvC4ofokDQKL6Txi4o1J2GqPrG/0EdIYf+Ti1PA1lDhwYeM=@D5mkN9u5xqftuPnvAXkF/125vb9bEYwJ2MNb4U5wg1wgHtAwzsRhwCOlfaOvfwPF0Epx21lY+n0O8pZyg7FKRRPPYbLHOg7KdYgndfgTFw1BqT6cIu3kF/A+hti2DOnllSKZ+XLIR/ZPSPVC85hGkR12A5X9Mu0PxRcsnx9SIo0=@Kdf0CrxKENR/J68Yi2uI5gC3nG/LX9DfP1CXSpCKmCOoHf6ZHNtC/QKnASKz6+6VRN11BhkgQm/LWUhJfWzWZf6fLg51M0QFL/FUfO9SATFo5CxUA3N8wZGyJzhD9ifksaUvO7TTjYUXvaN0vQQ9Gp7arcQEgK21m3mp04UNnh8=',
            'modeID': 0,
            'houseFunctionId': 0,
            'unitType': '',
            'houseStatusId': 0,
            'totalAreaId': 0,
            'inAreaId': 0,
            'buildingId': 100000125958
        }

        body = urllib.parse.urlencode(body)
        yield scrapy.Request(url=self.start_urls[0], method='POST', body=body, dont_filter=True, headers=self.headers)
