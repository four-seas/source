__author__ = 'ccinn'
__date__ = '20/8/19 21:51'

import re


class FirstAndTrim(object):
    def __init__(self, default=''):
        self.default = default

    def __call__(self, values):
        if isinstance(values, list) and len(values) > 0:
            value = values[0]
            if isinstance(value, str):
                return value.strip()
        else:
            return values


class ExtractValidContent(object):
    def __init__(self, regex=r'[^\s\\n]+'):
        self.regex = regex

    def __call__(self, values):
        if isinstance(values, str) and len(values) > 0:
            contents = re.compile(r"[^\s\\n]+").findall(values)
            return "".join(contents)
        else:
            return values


def default_missing_keys(item, default_value='', except_keys=[]):
    missing_keys = list(set(item.fields.keys()) - set(item.keys()))
    for missing_key in missing_keys:
        if except_keys:
            if missing_key not in except_keys:
                item[missing_key] = default_value
        else:
            item[missing_key] = default_value
