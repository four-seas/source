# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
from scrapy.utils.python import to_bytes
import hashlib
import scrapy
from scrapy.loader import ItemLoader
from source.sites.common.save_images_item import SaveImagesItem


class MysqlTwistedPipeline(object):
    """
    通用的数据库保存Pipeline
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        db_parms = dict(
            host=settings["MYSQL_HOST"],
            port=settings["MYSQL_PORT"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8mb4',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        # 连接池ConnectionPool
        dbpool = adbapi.ConnectionPool("MySQLdb", **db_parms)

        # 此处相当于实例化pipeline, 要在init中接收。
        return cls(dbpool)

    def process_item(self, item, spider):
        """
        使用twisted将mysql插入变成异步执行
        参数1: 我们每个item中自定义一个函数,里面可以写我们的插入数据库的逻辑
        """

        query = self.dbpool.runInteraction(self.do_insert, item)
        # 添加自己的处理异常的函数
        query.addErrback(self.handle_error, item, spider)

        # 最后一个pipeline，那么该item将会在终端输出，否则将传递给下一个pipeline
        # return item

    def do_insert(self, cursor, item):
        """
        执行具体的插入
        根据不同的item 构建不同的sql语句并插入到mysql中
        """
        insert_sql, params = item.save_to_mysql()
        affect_row = cursor.execute(insert_sql, params)

        inserted_id = cursor.lastrowid

        for url_path in item['image_paths']:
            item_loader = ItemLoader(item=SaveImagesItem())
            item_loader.add_value('house_id', inserted_id)
            item_loader.add_value('path', url_path[1])
            item_loader.add_value('url', url_path[0])
            save_image_item = item_loader.load_item()
            insert_sql, params = save_image_item.save_to_mysql()

            affect_row = cursor.execute(insert_sql, params)

    @staticmethod
    def handle_error(failure, item, spider):
        # 处理异步插入的异常
        print(failure)


class ImgDownloadPipeline(ImagesPipeline):
    image_dir = 'full'

    def get_media_requests(self, item, info):
        headers = item.get_images_headers()

        images_urls = [x for x in item['image_urls'] if x != '']
        self.image_dir = item.get_image_dir()
        for image_url in images_urls:
            # cdn加了反而下载失败
            # headers['referer'] = image_url
            yield scrapy.Request(image_url, headers=headers)

    def item_completed(self, results, item, info):
        """
        [(True,
          {'checksum': '2b00042f7481c7b056c4b410d28f33cf',
           'path': 'full/0a79c461a4062ac383dc4fade7bc09f1384a3910.jpg',
           'url': 'http://www.example.com/files/product1.pdf'}),
         (False,
          Failure(...))]
        """
        image_paths = [(x['url'], x['path']) for ok, x in results if ok]

        item['image_paths'] = image_paths

        return item

    def file_path(self, request, response=None, info=None):
        # start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('ImagesPipeline.image_key(url) and file_key(url) methods are deprecated, '
                          'please use file_path(request, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from image_key or file_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        # detect if file_key() or image_key() methods have been overridden
        if not hasattr(self.file_key, '_base'):
            _warn()
            return self.file_key(url)
        elif not hasattr(self.image_key, '_base'):
            _warn()
            return self.image_key(url)
        # end of deprecation warning block

        image_guid = hashlib.sha1(to_bytes(url)).hexdigest()  # change to request.url after deprecation

        return self.image_dir + '/%s.jpg' % (image_guid)
