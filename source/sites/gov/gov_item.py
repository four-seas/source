__author__ = 'ccinn'
__date__ = '22/4/21 0:20'

import scrapy
from source.utils.processors import FirstAndTrim
from source.items import MysqlItem
from source.utils.mysql_utils import *


class GovProjectItem(scrapy.Item, MysqlItem):
    table_name = 'project'

    field_list = [
        'name',
        'developer', 'licence',
        'sold_out', 'unsold',
        'supervision', 'area',
        'create_time', 'address',
        'update_time'
    ]

    duplicate_key_update = [
        'licence', 'developer',
        'name'
    ]

    name = scrapy.Field(
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
    address = scrapy.Field(
        output_processor=FirstAndTrim()
    )

    def clean_data(self):
        pass

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
