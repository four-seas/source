__author__ = 'ccinn'
__date__ = '22/4/21 0:20'

import scrapy
from source.utils.processors import FirstAndTrim
from source.items import MysqlItem
from source.utils.mysql_utils import *
import datetime


class GovMcItem(scrapy.Item, MysqlItem):
    table_name = 'market_control'

    field_list = [
        'attachment',
        'project_id', 'unit_number',
        'unit_type', 'unit_total_area',
        'unit_house_type', 'status',
        'charge', 'date',
        'building_id',
        'building',
        'address',
        'recordtion',
        'area',
        'area_number'
    ]

    duplicate_key_update = [
        'attachment',
        'unit_type', 'unit_total_area',
        'unit_house_type', 'status',
        'recordtion',
        'charge', 'address',
        'area',
        'area_number'
    ]

    attachment = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    project_id = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    unit_number = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    unit_type = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    unit_total_area = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    unit_house_type = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    status = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    charge = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    date = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    building = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    building_id = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    address = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    recordtion = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    area = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    area_number = scrapy.Field(
        output_processor=FirstAndTrim()
    )

    status_enums = {
        '不可销售': 0,
        '预售可售': 1,
        '确权不可售': 2,
        '确权可售': 3,
        '已过户': 4,
        '强制冻结': 5,
    }

    unit_type_enums = {
        '其他': 1,
        '住宅': 2,
        '商业': 3,
    }

    def clean_data(self):
        self['attachment'] = 0 if self['attachment'] == '否' else 1
        self['charge'] = 0 if self['charge'] == '否' else 1
        self['status'] = self.status_enums[self['status']]
        # self['unit_total_area'] = float(self['unit_total_area'])
        self['unit_number'] = int(self['unit_number'])
        self['unit_type'] = self.unit_type_enums[self['unit_type']]
        self['recordtion'] = int(self['recordtion'])

        self['date'] = str(datetime.date.today())

    def save_to_mysql(self):
        insert_sql, params_eval, _, _ = create_insert_sql(self.field_list, self.duplicate_key_update, self.table_name)
        self.clean_data()
        sql_params = eval(params_eval)

        return insert_sql, sql_params

    def help_fields(self):
        for field in self.fields:
            print(field, "= scrapy.Field()")


if __name__ == '__main__':
    instance = GovMcItem()
    print(instance.help_fields())
    print("*" * 30)
    print("self.data_clean()")
    sql, params, _, _ = create_insert_sql(field_list=instance.field_list,
                                          duplicate_key_update=instance.duplicate_key_update,
                                          table_name=instance.table_name)
    print(sql)
    print()
    print(params)
