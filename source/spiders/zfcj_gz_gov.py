__author__ = 'ccinn'
__date__ = '22/04/21 14:49'

# -*- coding: utf-8 -*-
import re
import urllib
from datetime import datetime
import js2xml
from js2xml.utils.vars import get_vars
import scrapy
from urllib import parse
from scrapy.loader import ItemLoader
from source.sites.gov.gov_item import GovProjectItem
from source.sites.gov.gov_mc_item import GovMcItem
import logging
import time
import scrapy
from scrapy.selector import Selector
from source.utils.strings_utils import rsa_encrypt

logger = logging.getLogger('my_logger')
import json


class ZfcjGzGovSpider(scrapy.Spider):
    name = 'zfcj_gz_gov'
    allowed_domains = ['zfcj.gz.gov.cn']
    # start_urls = ['http://zfcj.gz.gov.cn/zfcj/fyxx/xmxkbxxView']
    # start_urls = ['http://zfcj.gz.gov.cn/zfcj/fyxx/xmxkbxxList']
    start_urls = [
        'http://zfcj.gz.gov.cn/zfcj/fyxx/fdcxmxxRequest',  # 首页搜索
        'http://zfcj.gz.gov.cn/zfcj/fyxx/ysz',  # 详情页-预售证页面
        'http://zfcj.gz.gov.cn/zfcj/fyxx/xkb',  # 详情页-销控表页面
        'http://zfcj.gz.gov.cn/zfcj/fyxx/xmxkbxxList',  # 详情页-销控表-list页面
    ]
    headers = [
        {
            "HOST": "zfcj.gz.gov.cn",
            "Referer": "http://zfcj.gz.gov.cn/zfcj/fyxx/fdcxmxx",
            'Origin': 'http://zfcj.gz.gov.cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Upgrade-Insecure-Requests': 1,
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/68.0.3440.106 Safari/537.36"
        },
        {
            "HOST": "zfcj.gz.gov.cn",
            "Referer": "http://zfcj.gz.gov.cn/zfcj/fyxx/projectdetail",
            'Origin': 'http://zfcj.gz.gov.cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Upgrade-Insecure-Requests': 1,
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/68.0.3440.106 Safari/537.36"
        }
    ]

    def start_requests(self):
        # 搜索 "开发商"
        body = {
            "sProjectName": "",
            "sProjectAddress": "",
            "sPresellNo": "",
            "sDeveloper": "广州宏祥",
            "page": 1,
            "pageSize": 99
        }
        qs = urllib.parse.urlencode(body)
        url = f'{self.start_urls[0]}?{qs}'
        header = self.headers[0]
        yield scrapy.Request(url=url, dont_filter=True, headers=header)

    def parse(self, response: scrapy.http.Response):
        # 处理所有注册的楼盘项目
        """
{
        "data": [
            {
                "presell": null,
                "developerId": "50779",
                "houseUnsaleNum": "182",
                "projectAddress": "黄埔区云埔街",
                "developer": "广州宏祥房地产有限公司",
                "houseSoldNum": "0",
                "projectName": "东峪花园N8栋",
                "projectId": "35d0fb8eb1744e35b18053ddcd7e1e71"
            }
        ],
        "totalNum": 12,
        "totalPage": 1,
        "pageSize": 99,
        "currentPage": 1,
        "message": "ok",
        "status": 1
}
        """
        ret = json.loads(response.body)
        if ret['status'] != 1:
            logger.error('[%s] [%s]', response.url, ret['message'])

        data = ret['data']

        for item in data:
            item_loader = ItemLoader(item=GovProjectItem())
            item_loader.add_value('pid', item['projectId'])
            item_loader.add_value('name', item['projectName'])
            item_loader.add_value('developer_id', item['developerId'])
            item_loader.add_value('developer', item['developer'])
            item_loader.add_value('licence', item['presell'])
            item_loader.add_value('sold_out', item['houseSoldNum'])
            item_loader.add_value('unsold', item['houseUnsaleNum'])
            item_loader.add_value('address', item['projectAddress'])

            meta = {'item_loader': item_loader}
            # 如果没有预售证，则不进行爬其他信息了。
            if item['presell'] is None:
                yield item_loader.load_item()
                continue

            # Step2. 详情页-预售证页面
            body = {
                "sProjectId": item['projectId'],
                "sPreSellNo": item['presell'],
            }
            qs = urllib.parse.urlencode(body)
            url = f'{self.start_urls[1]}?{qs}'
            header = self.headers[1]
            yield scrapy.Request(url=url, method='GET', meta=meta, dont_filter=True,
                                 headers=header,
                                 callback=self.do_detail_ysz)


            # Step3. 详情页-销控表页面
            body = {
                "sProjectId": item['projectId'],
                "sPreSellNo": item['presell'],
            }
            qs = urllib.parse.urlencode(body)
            url = f'{self.start_urls[2]}?{qs}'
            header = self.headers[1]
            yield scrapy.Request(url=url, method='GET', meta=item, dont_filter=True,
                                 headers=header,
                                 callback=self.do_detail_xkb)

    def do_detail_ysz(self, response):
        item_loader = response.meta['item_loader']
        item_loader = ItemLoader(item=item_loader.load_item(), response=response)
        item_loader.add_xpath('send_licence', "//table[1]//tr[7]/td[6]//p/text()")
        s = Selector(response=response)
        accounts = s.xpath('//table[3]//tr[position()>2]/td[2]/text()').getall()
        banks = s.xpath('//table[3]//tr[position()>2]/td[3]/text()').getall()
        d = dict(zip(banks, accounts))
        dv = json.dumps(d, ensure_ascii=False)
        item_loader.add_value('charge', dv)
        yield item_loader.load_item()

    def do_detail_xkb(self, response):
        item = response.meta
        buildingIds = response.xpath('//*[@id="buildingId"]/@value').getall()
        script = response.xpath('//script[contains(text(), "var ak")]').get()
        ak = re.findall('var ak = "(.+)";', script)
        ak = ak[0]
        for buildingId in buildingIds:
            body = {
                'sProjectId': item['projectId'],
                'modeID': 0,
                'houseFunctionId': 0,
                'unitType': '',
                'houseStatusId': 0,
                'totalAreaId': 0,
                'inAreaId': 0,
                'buildingId': buildingId
            }
            token = rsa_encrypt(str(body['sProjectId']), ak)+"@"+rsa_encrypt(str(body['buildingId']),ak)+"@"+rsa_encrypt(str(body['houseFunctionId']),ak)+"@"+rsa_encrypt(str(body['unitType']),ak)+"@"+rsa_encrypt(str(body['houseStatusId']),ak)+"@"+rsa_encrypt(str(body['totalAreaId']),ak)+"@"+rsa_encrypt(str(body['inAreaId']),ak)
            body['token'] = token
            # print(body)

            body = urllib.parse.urlencode(body)
            yield scrapy.Request(url=self.start_urls[3], method='POST', meta=item, body=body, dont_filter=True, headers=self.headers[0],
                                 callback=self.do_crawler_detail)

    def do_crawler_detail(self, response: scrapy.http.Response):
        item = response.meta
        pid = item['projectId']
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
        n = len(response.xpath('//table//th//text()').getall())
        # 数据
        item_list = response.xpath('//table//td//text()').getall()
        item_list = [item_list[i:i + n] for i in range(0, len(item_list), n)]
        for item in item_list:
            item_loader = ItemLoader(item=GovMcItem())
            item_loader.add_value('project_id', pid)
            for key in m:
                if key in m.keys():
                    item_loader.add_value(key, item[m[key]])
            it = item_loader.load_item()
            yield it
