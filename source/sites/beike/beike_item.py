__author__ = 'ccinn'
__date__ = '20/8/19 0:20'

import scrapy
from source.items import MysqlItem
from source.utils.mysql_utils import *


class BeikeItem(scrapy.Item, MysqlItem):
    table_name = 'sources'

    field_list = [
        'title', 'total_price',
        'total_area', 'unit_price_value',
        'community_name', 'area',
        'addr', 'door_model',
        'has_elevator', 'has_subway',
        'toward', 'establish',
        'spider_src_url', 'spider_type'
    ]

    duplicate_key_update = [
        'total_price'
    ]

    title = scrapy.Field()
    total_price = scrapy.Field()
    total_area = scrapy.Field()
    unit_price_value = scrapy.Field()
    community_name = scrapy.Field()
    area = scrapy.Field()
    addr = scrapy.Field()
    door_model = scrapy.Field()
    has_elevator = scrapy.Field()
    has_subway = scrapy.Field()
    toward = scrapy.Field()
    establish = scrapy.Field()
    spider_src_url = scrapy.Field()
    spider_type = scrapy.Field()

    def clean_data(self):
        self['spider_type'] = 1

    def save_to_mysql(self):
        insert_sql, params_eval, _, _ = create_insert_sql(self.field_list, self.duplicate_key_update, self.table_name)
        self.clean_data()
        sql_params = eval(params_eval)

        return insert_sql, sql_params

    def help_fields(self):
        for field in self.fields:
            print(field, "= scrapy.Field()")


if __name__ == '__main__':
    instance = BeikeItem()
    print(instance.help_fields())
    print("*" * 30)
    print("self.data_clean()")
    sql, params, _, _ = create_insert_sql(field_list=instance.field_list,
                                          duplicate_key_update=instance.duplicate_key_update,
                                          table_name=instance.table_name)
    print(sql)
    print(params)
