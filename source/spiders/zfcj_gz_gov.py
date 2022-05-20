__author__ = 'ccinn'
__date__ = '22/04/21 14:49'

# -*- coding: utf-8 -*-
import re
import urllib
import scrapy
from urllib import parse
from scrapy.loader import ItemLoader
from source.sites.gov.gov_item import GovProjectItem
from source.sites.gov.gov_mc_item import GovMcItem
import logging
import scrapy
from scrapy.selector import Selector
from source.utils.strings_utils import rsa_encrypt

logger = logging.getLogger('zfcj_gz_gov_spider')
import json
import copy


class ZfcjGzGovSpider(scrapy.Spider):
    name = 'zfcj_gz_gov'
    allowed_domains = ['zfcj.gz.gov.cn']
    # start_urls = ['http://zfcj.gz.gov.cn/zfcj/fyxx/xmxkbxxView']
    # start_urls = ['http://zfcj.gz.gov.cn/zfcj/fyxx/xmxkbxxList']
    start_urls = [
        'http://zfcj.gz.gov.cn/zfcj/fyxx/fdcxmxxRequest',  # 首页搜索
        'http://zfcj.gz.gov.cn/zfcj/fyxx/ysz',  # 详情页-预售证页面
        'http://zfcj.gz.gov.cn/zfcj/fyxx/xkb',  # 详情页-销控表页面
        'http://zfcj.gz.gov.cn/zfcj/fyxx/xmxkbxxView',  # 详情页-销控表-view页面
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
        logger = logging.getLogger(response.url)
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
            item_loader.add_value('licence', item['presell'] if item['presell'] is not None else '0')
            item_loader.add_value('sold_out', item['houseSoldNum'])
            item_loader.add_value('unsold', item['houseUnsaleNum'])
            item_loader.add_value('address', item['projectAddress'])

            logger.info(item)
            meta = {'item_loader': item_loader}
            # 如果没有预售证，则不进行爬其他信息了。
            if item['presell'] is None:
                item_loader.add_value('charge', '')
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
            yield scrapy.Request(url=url, method='GET', meta=copy.deepcopy(item), dont_filter=True,
                                 headers=header,
                                 callback=self.do_detail_xkb)

    def do_detail_ysz(self, response):
        logger = logging.getLogger(response.url)
        item_loader = response.meta['item_loader']
        item_loader = ItemLoader(item=item_loader.load_item(), response=response)
        item_loader.add_xpath('send_licence', "//table[1]//tr[7]/td[6]//p/text()")
        s = Selector(response=response)
        accounts = s.xpath('//table[3]//tr[position()>2]/td[2]/text()').getall()
        banks = s.xpath('//table[3]//tr[position()>2]/td[3]/text()').getall()
        d = dict(zip(banks, accounts))
        dv = json.dumps(d, ensure_ascii=False)
        item_loader.add_value('charge', dv)
        logger.info(item_loader.load_item())
        yield item_loader.load_item()

    def do_detail_xkb(self, response):
        logger = logging.getLogger(response.url)
        item = response.meta

        # 获取幢
        all_full_name = response.xpath('//table/tr[3]/td/table/tr//td/text()').getall()
        # if item['projectId'] == '100000023707':
        #     logger.info(all_full_name)
        #     exit(1)
        buildings = []
        addresses = []
        for idx, v in enumerate(all_full_name):
            if idx % 2 == 0:
                continue
            # logger.info(v)
            # building = re.findall('(.+)\\(+?.*?([a-zA-Z][0-9]+)', v)
            building = re.findall('([a-zA-Z][0-9]+)', v)
            building = ''.join(list(set(building)))

            address = re.findall('[^(]+', v)
            address = address[0] if len(address) > 0 else ''

            # if len(building) > 0:
            #     if len(building[0]) > 1:
            #         address = building[0][0]
            #         building = building[0][1]
            #     elif len(building[0]) > 0:
            #         address = building[0][0]
            #         building = ''
            #     else:
            #         address = v
            #         building = ''
            # else:
            #     address = v
            #     building = ''
            addresses.append(address)
            buildings.append(building)

        buildingIds = response.xpath('//*[@id="buildingId"]/@value').getall()
        logger.info(buildingIds)
        # 获取token加密的公钥
        script = response.xpath('//script[contains(text(), "var ak")]').get()
        ak = re.findall('var ak = "(.+)";', script)
        ak = ak[0]
        for idx, buildingId in enumerate(buildingIds):
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
            token = rsa_encrypt(str(body['sProjectId']), ak) + "@" + rsa_encrypt(str(body['buildingId']), ak) + "@" + rsa_encrypt(
                str(body['houseFunctionId']), ak) + "@" + rsa_encrypt(str(body['unitType']), ak) + "@" + rsa_encrypt(
                str(body['houseStatusId']), ak) + "@" + rsa_encrypt(str(body['totalAreaId']), ak) + "@" + rsa_encrypt(
                str(body['inAreaId']), ak)
            body['token'] = token
            # print(body)

            item['building_id'] = buildingId
            item['building'] = buildings[idx]
            item['address'] = addresses[idx]
            body = urllib.parse.urlencode(body)
            meta = {
                'item': copy.deepcopy(item),
                'body': body
            }
            yield scrapy.Request(url=self.start_urls[3], method='POST', meta=meta, body=body, dont_filter=True,
                                 headers=self.headers[0],
                                 callback=self.do_detail_view)

    def do_detail_view(self, response: scrapy.http.Response):
        meta = response.meta
        body = meta['body']
        item = meta['item']

        beian = response.xpath('//table[1]//font/text()').getall()
        new_beian_list = []
        for a in beian:
            na = a.lstrip('\r\n\t                                            ')
            new_beian_list.append(na)

        item['beian_list'] = new_beian_list

        yield scrapy.Request(url=self.start_urls[4], method='POST', meta=copy.deepcopy(item), body=body, dont_filter=True,
                             headers=self.headers[0],
                             callback=self.do_detail_list)

    def do_detail_list(self, response: scrapy.http.Response):
        item = response.meta
        pid = item['projectId']
        building_id = item['building_id']
        licence = item['presell']
        building = item['building'] if str(item['building_id']) != '100000121046' else 'J3'
        area = ''
        area_number = '0'
        try:
            area = building[0]
            area_number = building[1:]
            try:
                int(area_number)
            except ValueError:
                area_number = '0'
        except:
            pass
        address = item['address']
        beian_list = item['beian_list']
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
        for idx, item in enumerate(item_list):
            item_loader = ItemLoader(item=GovMcItem())
            item_loader.add_value('project_id', pid)
            item_loader.add_value('building_id', building_id)
            item_loader.add_value('building', building)
            item_loader.add_value('address', address)
            item_loader.add_value('area', area)
            item_loader.add_value('area_number', area_number)
            if beian_list[idx].find('■') != -1:
                item_loader.add_value('recordtion', '1')
            else:
                item_loader.add_value('recordtion', '0')
            for key in m:
                if key in m.keys():
                    item_loader.add_value(key, item[m[key]])
            item_loader.add_value('licence', licence)
            it = item_loader.load_item()
            yield it
