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
```