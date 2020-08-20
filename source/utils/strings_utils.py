__author__ = 'ccinn'
__date__ = '20/8/19 08:51'

import datetime
import re


def str2date(value):
    """字符串转换时间方法"""
    try:
        value.strip().replace("·", "").strip()
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


def get_nums(value):
    """获取字符串内数字方法"""
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


def get_float_nums(value):
    """获取字符串内数字方法"""
    match_re = re.match(".*?(\d+(.?\d+)?).*", value)
    if match_re:
        nums = float(match_re.group(1))
    else:
        nums = 0

    return nums


def return_value(value):
    """直接获取值方法"""
    return value


def exclude_none(value):
    """排除none值"""
    if value:
        return value
    else:
        value = "无"
        return value


def extract_schema_domain_from_url(url):
    """Get domain name from url"""
    from urllib.parse import urlparse
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
    return domain
