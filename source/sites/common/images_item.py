__author__ = 'ccinn'
__date__ = '20/8/20 0:20'

import scrapy
from scrapy.loader.processors import Compose
from source.utils.processors import FirstAndTrim, ExtractValidContent
from source.items import MysqlItem, ImageItem
from source.utils.mysql_utils import *
from source.utils.strings_utils import *


class ImagesItem(scrapy.Item, MysqlItem, ImageItem):
    table_name = 'houses'

    field_list = [
        'master_id',
        'title', 'total_price',
        'total_area', 'unit_price_value',
        'community_name', 'area',
        'addr', 'door_model',
        'has_elevator', 'has_subway',
        'toward', 'establish',
        'spider_src_url', 'spider_type'
    ]

    duplicate_key_update = [
        'title', 'total_price',
        'total_area', 'unit_price_value',
        'community_name', 'area',
        'addr', 'door_model',
        'has_elevator', 'has_subway',
        'toward', 'establish',
    ]

    master_id = scrapy.Field()
    title = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    total_price = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    total_area = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    unit_price_value = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    community_name = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    area = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    addr = scrapy.Field(
        output_processor=Compose(FirstAndTrim(), ExtractValidContent())
    )
    door_model = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    has_elevator = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    has_subway = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    toward = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    establish = scrapy.Field(
        output_processor=FirstAndTrim()
    )
    spider_src_url = scrapy.Field()
    spider_type = scrapy.Field()

    # image-pipeline
    image_urls = scrapy.Field()
    images = scrapy.Field()
    image_paths = scrapy.Field()

    def clean_data(self):

        self['total_price'] = get_nums(self['total_price'])
        self['total_area'] = get_float_nums(self['total_area'])
        self['unit_price_value'] = get_float_nums(self['unit_price_value'])
        self['establish'] = get_nums(self['establish'])

        if 'has_elevator' in self and self['has_elevator'] == '有':
            self['has_elevator'] = 1
        else:
            self['has_elevator'] = 0

        if 'has_subway' in self and isinstance(self['has_subway'], str):
            self['has_subway'] = 1
        else:
            self['has_subway'] = 0

        # add_value
        self['master_id'] = self['master_id'][0]
        self['spider_src_url'] = self['spider_src_url'][0]
        self['spider_type'] = self['spider_type'][0]

    def save_to_mysql(self):
        insert_sql, params_eval, _, _ = create_insert_sql(self.field_list, self.duplicate_key_update, self.table_name)
        self.clean_data()
        sql_params = eval(params_eval)

        return insert_sql, sql_params

    def get_image_dir(self):
        return 'beike'

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
