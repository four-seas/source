__author__ = 'ccinn'
__date__ = '20/8/19 08:51'

import datetime
import re
import base64
import rsa

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

def _str2key(s):
    # 对字符串解码
    b_str = base64.b64decode(s)

    if len(b_str) < 162:
        return False

    hex_str = ''

    # 按位转换成16进制
    for x in b_str:
        h = hex(x)[2:]
        h = h.rjust(2, '0')
        hex_str += h

    # 找到模数和指数的开头结束位置
    m_start = 29 * 2
    e_start = 159 * 2
    m_len = 128 * 2
    e_len = 3 * 2

    modulus = hex_str[m_start:m_start + m_len]
    exponent = hex_str[e_start:e_start + e_len]

    return modulus, exponent


def rsa_encrypt(s, pubkey_str):
    '''
    rsa加密
    :param s:
    :param pubkey_str:公钥
    :return:
    '''
    key = _str2key(pubkey_str)
    modulus = int(key[0], 16)
    exponent = int(key[1], 16)
    pubkey = rsa.PublicKey(modulus, exponent)
    return base64.b64encode(rsa.encrypt(s.encode(), pubkey)).decode()