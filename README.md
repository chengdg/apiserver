# apiserver: 微商城后端API Server #

## 源码文档 ##
用Doxygen生成文档：`doxygen Doxygen`。也可以直接访问[在线文档](http://s01.gaoliqi.com:82/doc/apiserver)（由[weapp_apiserver_doc](http://s01.gaoliqi.com:8081/jenkins/job/weapp_apiserver_doc/)自动构建）。

## 启动 API server ##

安装必要的组件：
```
pip install --upgrade falcon peewee "pymongo==2.5"
```

像Django一样启动falcon API server：
```
python manage.py runserver 0.0.0.0 8004
```

## API调试Console ##

```
http://localhost:8001/console/
```

> **数据**部分的遵循JavaScript语法。变量必须是`data`。


## BDD测试 ##

BDD测试时，需要准备微商城的数据。而这些操作在Weapp项目已经实现。为了避免重复开发、复用已有的step，本项目BDD测试会先在Weapp环境下执行初始化数据的测试场景，然后在本项目环境下执行测试场景的step。具体分2步：

1. 搜集`:weapp` step并汇集到一起，在Weapp源码环境下执行，初始化数据。需要预先导出Weapp源码到`../weapp`目录下。如需修改weapp源码目录，在settings.py中修改`WEAPP_DIR`。

2. 在本项目中执行不含`:weapp`的测试step。即含有`:weapp`的step在本项目测试时会被忽略。

需要注意的是，带有`:weapp`的step只能在不带`:weapp`之前。目前不支持含`:weapp`step与正常step交替出现的场景(Scenario)。

测试时，只需在`apiserver`目录下执行`behave -k`即可。

BDD测试需要behave、selenium等Python包的支持。


## 参考资料 ##

[WAPI文档](http://git.weizzz.com:8082/weizoom/Weapp/wikis/WAPI_home)

## 如何集成到Ningx？ ##
1. 在hosts文件中添加如下域名
```
127.0.0.1 api.weapp.com
```
2. 编辑Nginx的`nginx.conf`文件，添加如下配置
```py
server {
    listen       80;
    server_name  api.weapp.com;

    #charset koi8-r;

    #access_log  logs/api_weapp.access.log  main;
    location /static {
        root d:/anthole/anthole/apiserver/; #换成自己的目录
    }
    
    location / {
        proxy_pass http://127.0.0.1:8001;
    }
    
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   html;
    }
}
```
