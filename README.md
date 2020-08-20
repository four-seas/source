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