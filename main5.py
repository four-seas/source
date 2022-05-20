import datetime
import MySQLdb

import xlsxwriter


def maxLength(a, b):
    if a > b:
        return a
    else:
        return b


if __name__ == '__main__':
    cur_date = str(datetime.date.today())
    excel_file = f'(阳光家缘)中央城数据统计-{cur_date}.xlsx'
    workbook = xlsxwriter.Workbook(excel_file)

    db = MySQLdb.connect(host="127.0.0.1", port=3306, db="gov", user="root", password="123456", charset='utf8')

    # cursor = db.cursor(MySQLdb.cursors.DictCursor)
    cursor = db.cursor()

    header_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'align': 'center',  # 水平居中
        'valign': 'vcenter',  # 垂直居中
        'fg_color': '#AEEEEE',  # 颜色填充
    })

    border = workbook.add_format({'border': 1})

    # 总备案统计
    worksheets = []
    worksheets.append(workbook.add_worksheet('当天各幢备案统计'))
    worksheets.append(workbook.add_worksheet('所有幢备案汇总'))
    worksheets.append(workbook.add_worksheet('对比昨天新增备案户'))
    worksheets.append(workbook.add_worksheet('对比昨天新增备数量'))
    worksheets.append(workbook.add_worksheet('累户已备案业主'))
    worksheets.append(workbook.add_worksheet('查看已出预售证监管账号'))

    sqls = []
    sql = """
-- 当天各幢备案统计
SELECT building AS '幢', GROUP_CONCAT(nc) AS '统计结果'
FROM (
	SELECT building, concat(CASE recordtion
			WHEN 0 THEN '未备案'
			ELSE '已备案'
		END, ':', c) AS nc
	FROM (
		SELECT building, recordtion, COUNT(1) AS c
		FROM market_control
		WHERE unit_type = 2
			AND `date` = curdate()
		GROUP BY recordtion, building
		ORDER BY recordtion DESC, building ASC
	) a
) b
GROUP BY building
    """
    sqls.append(sql)

    sql = """
-- 所有幢备案汇总
select 
  case recordtion when 0 then '未备案' else '已备案' end as '备案情况', 
  count(1) as '数量' 
from 
  market_control 
where 
  unit_type = 2 
  and `date` = curdate() 
group by 
  recordtion 
order by 
  recordtion desc;
"""
    sqls.append(sql)

    sql = """
-- 对比昨天新增备案户 
select 
  b.`building` as '幢', 
  b.unit_number as '房号' 
from 
  market_control as a 
  inner join market_control as b on a.project_id = b.project_id 
  and a.building_id = b.building_id 
  and a.unit_number = b.unit_number 
where 
  b.date = curdate() 
  and a.date = DATE_SUB(
    CURDATE(), 
    INTERVAL 1 DAY
  ) 
  and b.recordtion = 1 
  and a.recordtion = 0 
  and b.unit_type = 2 
order by 
  b.area asc, 
  b.area_number asc;
        """
    sqls.append(sql)

    sql = """
-- 对比昨天各幢新增备案数
select 
  `building` as '幢', 
  count(1) as '数量' 
from 
  (
    select 
      b.`building` 
    from 
      market_control as a 
      inner join market_control as b on a.project_id = b.project_id 
      and a.building_id = b.building_id 
      and a.unit_number = b.unit_number 
    where 
      b.date = curdate() 
      and a.date = DATE_SUB(
        CURDATE(), 
        INTERVAL 1 DAY
      ) 
      and b.recordtion = 1 
      and a.recordtion = 0 
      and b.unit_type = 2
  ) as t 
group by 
  `building`;
            """
    sqls.append(sql)

    sql = """
-- 已备案
select 
  building as '幢', 
  unit_number as '房号' 
from 
  market_control 
where 
  unit_type = 2 
  and recordtion = 1 
  and `date` = curdate() 
order by 
  area asc, 
  area_number asc;
            """
    sqls.append(sql)

    sql = """
-- 各栋抵押统计
SELECT building as '幢', GROUP_CONCAT(nc)  as '统计结果'
FROM (
	SELECT building, concat(CASE charge
			WHEN 1 THEN '已抵押'
			ELSE '未抵押'
		END, ':', c) AS nc
	FROM (
		SELECT building, charge, COUNT(1) AS c
		FROM market_control
		WHERE unit_type = 2
			AND `status` = 0
			AND `date` = curdate()
		GROUP BY charge, building
		ORDER BY charge DESC, building ASC
	) a
) b
GROUP BY building;
        """
    sqls.append(sql)

    sql = """
-- 查看已出预售证监管账号
select 
  address '地址', 
  charge as '监管账号' 
from 
  project 
where 
  licence > 0;
    """
    sqls.append(sql)

    for index, s in enumerate(sqls):
        col_max_length = []
        worksheet = worksheets[index]
        cursor.execute(s)
        data = cursor.fetchall()
        col_names = [i[0] for i in cursor.description]
        for idx, item in enumerate(col_names):
            worksheet.write(0, idx, item, header_format)
            worksheet.set_column(idx, idx, len(item.encode('utf-8')) + 2)
            col_max_length.append(len(item.encode('utf-8')) + 2)
        worksheet.autofilter(0, 0, 0, len(col_names) - 1)

        for idx, item in enumerate(data):
            i = 0
            while i < len(col_names):
                row_num = idx + 1
                col_num = i
                worksheet.write(row_num, col_num, item[i])
                l = maxLength(len(str(item[i]).encode('utf-8')) + 2, col_max_length[i])
                worksheet.set_column(i, i, l)

                i = i + 1

    workbook.close()
