# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from twisted.logger import Logger

log = Logger()


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
        query.addErrback(self.handle_error, item)

        # 最后一个pipeline，那么该item将会在终端输出，否则将传递给下一个pipeline
        return item

    def do_insert(self, cursor, item):
        """
        执行具体的插入
        根据不同的item 构建不同的sql语句并插入到mysql中
        """

        insert_sql, params = item.save_to_mysql()

        cursor.execute(insert_sql, params)
        #
        # inserted_id = cursor.lastrowid
        #
        # for url_path in item['image_paths']:
        #     item_loader = ItemLoader(item=SaveImagesItem())
        #     item_loader.add_value('house_id', inserted_id)
        #     item_loader.add_value('path', url_path[1])
        #     item_loader.add_value('url', url_path[0])
        #     save_image_item = item_loader.load_item()
        #     insert_sql, params = save_image_item.save_to_mysql()
        #
        #     affect_row = cursor.execute(insert_sql, params)

    @staticmethod
    def handle_error(failure, item):
        insert_sql, params = item.save_to_mysql(clean=False)
        #
        print(insert_sql, params)
        # 处理异步插入的异常
        print(failure)
