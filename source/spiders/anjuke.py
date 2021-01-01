# -*- coding: utf-8 -*-
import re
import scrapy

# 此脚本仅供学习参考，切莫用于商业用途
class AnjukeSpider(scrapy.Spider):
    name = 'anjuke'
    allowed_domains = ['anjuke.com']  # 允许爬取的范围

    # 最开始请求的url地址
    start_urls = ['https://guangzhou.anjuke.com/sale/?from=navigation']

    def parse(self, response):
        # print(response.text)
        # print(response.body)

        # 调试
        i = 0

        li_list = response.xpath('//div[@class="house-details"]')
        for li in li_list:
            # i += 1
            # if i > 1:
            #     break
            item = {}
            detail_url = li.xpath('./div[@class="house-title"]/a/@href').extract_first().strip()
            item['master_id'] = re.search(r'.+view/(\w+)', detail_url).group(1)
            item['spider_src_url'] = detail_url
            item['title'] = li.xpath('./div[@class="house-title"]/a/text()').extract_first().strip()

            # 详情
            yield scrapy.Request(
                detail_url,
                callback=self.parse_detail,
                meta={"item": item}
            )

        # 翻页
        next_url = response.xpath('//a[@class="aNxt"]/@href').extract_first()
        if next_url is not None:
            yield scrapy.Request(
                next_url,
                callback=self.parse,
            )

    def parse_detail(self, response):
        item = response.meta['item']
        item['total_price'] = float(response.xpath('//span[@class="light info-tag"]/em/text()').extract_first()) * 10000
        item['total_area'] = float(
            response.xpath('//span[@class="info-tag" and text()="平方米"]/em/text()').extract_first())
        tmp = response.xpath(
            '//div[@class="houseInfo-label text-overflow" and text()="房屋单价："]/../div[@class="houseInfo-content"]/text()').extract_first()
        item['unit_price_value'] = re.search(r'\d+', tmp).group()
        item['community_name'] = response.xpath(
            '//div[@class="houseInfo-label text-overflow" and text()="所属小区："]/parent::li//a/text()').extract_first()

        # 地址
        addr = ''.join(response.xpath('string(//p[@class="loc-text"])').extract_first().split())
        item['area'] = addr.split('－')[0]
        item['addr'] = addr

        # 房屋户型
        item['door_model'] = ''.join(response.xpath(
            '//div[@class="houseInfo-label text-overflow" and text()="房屋户型："]/parent::li/div[@class="houseInfo-content"]/text()').extract_first().split())

        # 是否有电梯
        has_elevator = response.xpath(
            '//div[@class="houseInfo-label text-overflow" and text()="配套电梯："]/parent::li/div[@class="houseInfo-content"]/text()') \
            .extract_first()
        if has_elevator is None:
            has_e = 2
        elif has_elevator == '有':
            has_e = 1
        else:
            has_e = 0
        item['has_elevator'] = has_e

        # has_subway 是否有地铁，无法确定
        item['has_subway'] = 2

        # 房屋朝向
        item['toward'] = response.xpath(
            '//div[@class="houseInfo-label text-overflow" and text()="房屋朝向："]/parent::li/div[@class="houseInfo-content"]/text()') \
            .extract_first()

        # 建造年代
        item['establish'] = response.xpath(
            '//div[@class="houseInfo-label text-overflow" and text()="建造年代："]/parent::li/div[@class="houseInfo-content"]/text()') \
            .extract_first() \
            .strip()

        yield item
