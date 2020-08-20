__author__ = 'ccinn'
__date__ = '20/8/20 0:20'

import scrapy
from source.items import MysqlItem
from source.utils.mysql_utils import *


class SaveImagesItem(scrapy.Item, MysqlItem):
    table_name = 'images'

    field_list = [
        'house_id',
        'path', 'url',
    ]

    duplicate_key_update = [
        'url'
    ]

    house_id = scrapy.Field()
    path = scrapy.Field()
    url = scrapy.Field()

    def clean_data(self):
        # add_value
        self['house_id'] = self['house_id'][0]
        self['path'] = self['path'][0]
        self['url'] = self['url'][0]

    def save_to_mysql(self):
        insert_sql, params_eval, _, _ = create_insert_sql(self.field_list, self.duplicate_key_update, self.table_name)
        self.clean_data()
        sql_params = eval(params_eval)

        return insert_sql, sql_params

    def help_fields(self):
        for field in self.field_list:
            print(field, "= scrapy.Field()")


if __name__ == '__main__':
    instance = SaveImagesItem()
    print(instance.help_fields())
    print("*" * 30)
    print("self.data_clean()")
    sql, params, _, _ = create_insert_sql(field_list=instance.field_list,
                                          duplicate_key_update=instance.duplicate_key_update,
                                          table_name=instance.table_name)
    print(sql)
    print(params)
