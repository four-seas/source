## Docker 开发

```shell
// 构建开发镜像
docker build -t source .

// 创建开发容器
docker run -it --name sourcec -v $(PWD):/www source:latest bash
// 记得退出容器

// 基于开发容器创建一个新镜像用于pycharm环境
docker commit -a "ccinn" -m "commit message" sourcec source-ide
```

在ide配置中找到`Project:source > Project Interpreter >>> add python interpreter > docker > images select source-ide`


```shell
// 回到环境中
docker start -i sourcec
```

## 开箱即用

### docker-composer

```
# 写入配置文件
cat <<EOF > config.py
MYSQL_HOST = 'mysql'
MYSQL_PORT = 3306
MYSQL_DBNAME = 'four_seas'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
EOF

# 启动容器s
docker-compose up
```

### k8s

- 由于k8s磁盘挂载需要使用绝对路径
- 所以此模板是我本人的磁盘目录，需要对应修改spec.template.volumes.*的路径
- sed -i "s#"$(PWD)"#{your's current dir path}#g" k8s-job.yaml

#### job

```
# 创建容器s
kubectl create -f k8s-job.yaml

# 查看pod状态
kubectl describe pod $(kubectl get pods --selector=job-name=beike --output=jsonpath={.items..metadata.name})

# 查看对应容器的日期
kubectl log $(kubectl get pods --selector=job-name=beike --output=jsonpath={.items..metadata.name}) source-beike

# 查看当前数据
kubectl exec -it $(kubectl get pods --selector=job-name=beike --output=jsonpath={.items..metadata.name}) -- mysql -u root -p'123456' -e 'select count(1) from four_seas.houses;'
+----------+
| count(1) |
+----------+
|      169 |
+----------+

# 查看具体数据
kubectl exec -it $(kubectl get pods --selector=job-name=beike --output=jsonpath={.items..metadata.name}) -- mysql -u root -p'123456' --default-character-set=utf8 -e 'select * from four_seas.houses limit 5;'

+----+--------------+----------------------------------------------------------------------------+-------------+------------+------------------+--------------------------------+--------+----------------------------------------------------+--------------+--------------+------------+------------+-----------+------------------------------------------------+-------------+---------------------+---------------------+
| id | master_id    | title                                                                      | total_price | total_area | unit_price_value | community_name                 | area   | addr                                               | door_model   | has_elevator | has_subway | toward     | establish | spider_src_url                                 | spider_type | created_at          | updated_at          |
+----+--------------+----------------------------------------------------------------------------+-------------+------------+------------------+--------------------------------+--------+----------------------------------------------------+--------------+--------------+------------+------------+-----------+------------------------------------------------+-------------+---------------------+---------------------+
|  1 | 108401545394 | 碧桂园豪进广场 4室1厅 南                                                   |      138.00 |     325.00 |         23514.90 | 碧桂园豪进广场                 | 增城   | (增城)东江大道南28号                               | 4室1厅2卫    |            1 |          0 | 南         |         0 | https://gz.ke.com/ershoufang/108401545394.html |           1 | 2020-08-28 03:16:32 | 2020-08-28 03:16:32 |
|  2 | 108401545480 | 新世界花园 嘉怡苑 花园景观三房 安静舒适 自住优选                           |      108.00 |     200.00 |         18458.70 | 新塘新世界花园嘉怡苑           | 增城   | (增城)花园东路新塘新世界花园嘉怡苑                 | 3室1厅2卫    |            0 |          1 | 北         |         0 | https://gz.ke.com/ershoufang/108401545480.html |           1 | 2020-08-28 03:16:33 | 2020-08-28 03:16:33 |
|  3 | 108401545864 | 云山居 3室2厅 东南                                                         |      105.00 |     308.00 |         29075.80 | 云山居                         | 白云   | (白云)云山街33号                                   | 3室2厅2卫    |            0 |          0 | 东南       |      2000 | https://gz.ke.com/ershoufang/108401545864.html |           1 | 2020-08-28 03:16:34 | 2020-08-28 03:16:34 |
|  4 | 108401521691 | 保利品质舒适享受高大小区~一线望江，南北对流大四房~                         |      167.00 |     346.00 |         20669.10 | 保利东江首府                   | 增城   | (增城)江府大道2号                                  | 4室2厅2卫    |            1 |          0 | 东南 南    |      2012 | https://gz.ke.com/ershoufang/108401521691.html |           1 | 2020-08-28 03:16:35 | 2020-08-28 03:16:35 |
|  5 | 108401545886 | 丽江花园如英居 3室1厅 西北                                                 |       94.00 |     330.00 |         35106.40 | 丽江花园如英居                 | 番禺   | (番禺)沿沙东路丽江花园如英居                       | 3室1厅1卫    |            1 |          1 | 西北       |      2008 | https://gz.ke.com/ershoufang/108401545886.html |           1 | 2020-08-28 03:16:36 | 2020-08-28 03:16:36 |
+----+--------------+----------------------------------------------------------------------------+-------------+------------+------------------+--------------------------------+--------+----------------------------------------------------+--------------+--------------+------------+------------+-----------+------------------------------------------------+-------------+---------------------+---------------------+
```