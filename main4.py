import datetime
import re

import MySQLdb

import xlsxwriter


def maxLength(a, b):
    if a > b:
        return a
    else:
        return b


if __name__ == '__main__':
    cur_date = str(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M"))
    excel_file = f'(阳光家缘)中央城数据统计-{cur_date}.xlsx'
    workbook = xlsxwriter.Workbook(excel_file)

    db = MySQLdb.connect(host="127.0.0.1", port=3306, db="gov", user="root", password="sb250!@#", charset='utf8')

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
    sqls = []

    sql = """
-- 各幢备案统计
select
  building as 幢,
  recordtion as '(0=未备案，1=已备案)是否备案',
  count(1) as '(未/已)备案数'
from
  market_control
where
  unit_type = 2
  and `status` = 0
  and `date` = curdate()
group by
  recordtion,
  building
order by
  recordtion desc,
  building asc;
    """
    sqls.append(sql)

    sql = """
-- 各幢备案汇总
select
  recordtion as '(0=未备案，1=已备案)是否备案',
  count(1) as '(未/已)备案数'
from
  market_control
where
  unit_type = 2
  and `status` = 0
  and `date` = curdate()
group by
  recordtion
order by
  recordtion desc;
"""
    sqls.append(sql)

    sql = """
-- 对比昨日新增备案业主
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
-- 对比昨日各幢新增备案数
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
-- 累计已备案业主
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
-- 对比昨日新增网签户
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
  and b.recordtion = 0
  and a.status = 1
  and b.status = 0
  and b.unit_type = 2
order by
  b.area asc,
  b.area_number asc;
                    """
    sqls.append(sql)

    sql = """
-- 累计已网签业主(排除备案)
select
  building as '幢',
  unit_number as '房号'
from
  market_control
where
  unit_type = 2
  and recordtion = 0
  and `status` = 0
  and `date` = curdate()
order by
  area asc,
  area_number asc;
                """
    sqls.append(sql)

    sql = """
-- 未网签(暂时可售)
select
  building as '幢',
  unit_number as '房号',
  unit_house_type as '户型',
  unit_total_area as '面积'
from
  market_control
where
  unit_type = 2
  and recordtion = 0
  and `status` = 1
  and `date` = curdate()
order by
  area asc,
  area_number asc;
                    """
    sqls.append(sql)

    sql = """
-- 各幢网签统计(排除备案)
select
  building as 幢,
  case `status` when 1 then 0 else 1 end as '(0=未网签，1=已网签)是否网签',
  count(1) as '(未/已)网签数'
from
  market_control
where
  unit_type = 2
  and (
    `status` = 0
    or `status` = 1
  )
  and recordtion = 0
  and `date` = curdate()
group by
  `status`,
  `building`
order by
  `status` asc,
  `building` asc;
                        """
    sqls.append(sql)

    sql = """
-- 各抵押统计
SELECT building AS '幢', charge AS '(0=未抵押, 1=已抵押)', COUNT(1) AS '(未/已)抵押数'
FROM market_control
WHERE unit_type = 2
	AND `status` = 0
	AND `date` = curdate()
GROUP BY charge, building
ORDER BY charge DESC, building ASC
        """
    sqls.append(sql)

    sql = """
-- 监管信息
SELECT a1.licence AS '预售证', b1.building AS '幢'
	, CASE a1.charge
		WHEN '{}' THEN '暂无'
		ELSE a1.charge
	END AS '监管账号', a1.address AS '项目地址'
FROM project a1
	RIGHT JOIN (
		SELECT b.licence, b.building
		FROM project a
			RIGHT JOIN market_control b ON a.licence = b.licence
		WHERE b.date = curdate()
			AND unit_type = 2
		GROUP BY b.licence, b.building
	) b1
	ON a1.licence = b1.licence
ORDER BY a1.licence
    """
    sqls.append(sql)

    for index, s in enumerate(sqls):
        task_name = re.findall('--\s+(.+)', s)
        task_name = task_name[0]
        worksheets.append(workbook.add_worksheet(task_name))

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
