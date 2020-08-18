__author__ = 'ccinn'
__date__ = '20/8/19 0:20'

field_list = ['title', 'url']
duplicate_key_update = ['total']


def create_insert_sql(field_list: list, duplicate_key_update: list, table_name: str):
    field_str = ""
    field_s = ""
    update_s = ""
    params_s = ""
    params = []
    params_eval = "("
    for field in field_list:
        field_str += field + ','
        field_s += '%s,'
        params_s += 'self["' + str(field) + '"],\n\t'
        params.append('self["' + str(field) + '"]')

    params_eval += ",".join(params) + ")"
    for duplicate_key in duplicate_key_update:
        update_s += str(duplicate_key) + "=VALUES(" + str(duplicate_key) + '),'
    params_txt = "params = (\n" + params_s + ")"
    sql_txt = "insert into {0}({1}) VALUES({2}) \n\t\t\t\t\t\t\t\t\t\tON DUPLICATE KEY UPDATE  {3}".format(table_name,
                                                                                                           field_str[
                                                                                                           :-1],
                                                                                                           field_s[:-1],
                                                                                                           update_s[
                                                                                                           :-1])

    sql = "insert into {0}({1}) VALUES({2}) ON DUPLICATE KEY UPDATE  {3}".format(table_name,
                                                                                 field_str[:-1],
                                                                                 field_s[:-1],
                                                                                 update_s[:-1])
    return sql, params_eval, sql_txt, params_txt


if __name__ == '__main__':
    sql, params, _, _ = create_sql(field_list, duplicate_key_update, "hourse")
    print(sql)
    print(params)
