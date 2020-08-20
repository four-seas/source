# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from abc import ABCMeta, abstractmethod


class SourceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BaseItem(metaclass=ABCMeta):
    """
    基础的每个Item都应该实现的接口
    """

    field_list = []  # 字段名

    @abstractmethod
    def clean_data(self):
        """
        对于原始提取字段进行清理
        :return:
        """
        pass

    @staticmethod
    @abstractmethod
    def help_fields(fields: list):
        """
        帮助生成field定义字段代码。
        :param fields:
        :return:
        """
        pass


class MysqlItem(BaseItem):
    """
    数据存取至mysql数据库应该实现的接口
    """
    table_name = ""  # 数据库表名
    duplicate_key_update = []  # "重复插入时，需要更新的字段"

    @abstractmethod
    def save_to_mysql(self):
        """
        生成插入数据库的sql语句
        :return:
        """
        pass


class ImageItem(metaclass=ABCMeta):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_paths = scrapy.Field()

    def get_images_headers(self):
        return {
            'upgrade-insecure-requests': 1,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        }

    @abstractmethod
    def get_image_dir(self):
        pass
