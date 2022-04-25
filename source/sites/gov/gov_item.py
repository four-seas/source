__author__ = 'ccinn'
__date__ = '22/4/21 0:20'

import time
from datetime import datetime

import scrapy
from source.utils.processors import FirstAndTrim
from source.items import MysqlItem
from source.utils.mysql_utils import *


class GovProjectItem(scrapy.Item, MysqlItem):
    table_name = 'project'

    field_list = [
        'pid',
        'name',
        'developer', 'developer_id', 'licence',
        'sold_out', 'unsold',
        'supervision',
        'create_time', 'address',
        'update_time',

        'send_licence',
        'charge'
    ]

    duplicate_key_update = [
        'name',
        'developer',  'licence',
        'sold_out', 'unsold',
        'supervision', 'address',
        'update_time',

        'send_licence',
        'charge'
    ]

    pid = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    name = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    developer_id = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    developer = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    licence = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    sold_out = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    unsold = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    supervision = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    create_time = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    update_time = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    address = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    send_licence = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    charge = scrapy.Field(
        output_processor=FirstAndTrim()
    )

    def clean_data(self):
        self['licence'] = int(self['licence']) if hasattr(self, 'licence') else 0
        self['sold_out'] = int(self['sold_out'])
        self['unsold'] = int(self['unsold'])
        self['supervision'] = self['supervision'] if hasattr(self, 'supervision') else ''

        if not hasattr(self, 'send_licence'):
            self['send_licence'] = ''
        else:
            self['send_licence'] = datetime.strftime(datetime.strptime(self['send_licence'], '%b %d, %Y'), '%Y-%m-%d') if self[
                                                                                                                              'send_licence'] is not None else ''
        if not hasattr(self, 'charge'):
            self['charge'] = ''

        self['create_time'] = int(time.time())
        self['update_time'] = int(time.time())

    def save_to_mysql(self):
        insert_sql, params_eval, _, _ = create_insert_sql(self.field_list, self.duplicate_key_update, self.table_name)
        self.clean_data()
        sql_params = eval(params_eval)

        return insert_sql, sql_params

    def help_fields(self):
        for field in self.fields:
            print(field, "= scrapy.Field()")


if __name__ == '__main__':
    instance = GovProjectItem()
    print(instance.help_fields())
    print("*" * 30)
    print("self.data_clean()")
    sql, params, _, _ = create_insert_sql(field_list=instance.field_list,
                                          duplicate_key_update=instance.duplicate_key_update,
                                          table_name=instance.table_name)
    print(sql)
    print(params)
