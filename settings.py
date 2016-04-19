# -*- coding: utf-8 -*-

import os
import logging

SERVICE_NAME = "H5"

DEBUG = True
PROJECT_HOME = os.path.dirname(os.path.abspath(__file__))

MODE = 'develop'

if MODE == 'develop':
    OPERATION_DB = 'weapp'
    OPERATION_USER = 'weapp'
    OPERATION_HOST = 'db.weapp.com'
else:
    OPERATION_DB = 'operation'
    OPERATION_USER = 'operation'
    OPERATION_HOST = 'db.operation.com'


DATABASES = {
    'default': {
        'ENGINE': 'mysql+retry',
        'NAME': 'weapp',
        'USER': 'weapp',                      # Not used with sqlite3.
        'PASSWORD': 'weizoom',                  # Not used with sqlite3.
        'HOST': 'db.weapp.com',
        'PORT': '',
        'CONN_MAX_AGE': 100
    },
    'watchdog': {
        'ENGINE': 'mysql+retry',
        'NAME': OPERATION_DB,
        'USER': OPERATION_USER,                      # Not used with sqlite3.
        'PASSWORD': 'weizoom',                  # Not used with sqlite3.
        'HOST': OPERATION_HOST,
        'PORT': '',
        'CONN_MAX_AGE': 100
    }
}


MIDDLEWARES = [
    'middleware.OAuth_middleware.OAuthMiddleware',
    'middleware.core_middleware.ApiAuthMiddleware',
    
    # 'middleware.debug_middleware.SqlMonitorMiddleware',
    # 'middleware.debug_middleware.RedisMiddleware',

    #账号信息中间件
    'middleware.webapp_account_middleware.WebAppAccountMiddleware',
]
#sevice celery 相关
EVENT_DISPATCHER = 'redis'

# settings for WAPI Logger
if MODE == 'develop':
    WAPI_LOGGER_ENABLED = True # Debug环境下不记录wapi详细数据
    WAPI_LOGGER_SERVER_HOST = 'mongo.weapp.com'
    WAPI_LOGGER_SERVER_PORT = 27017
    WAPI_LOGGER_DB = 'wapi'
    IMAGE_HOST = 'http://dev.weapp.com'
    PAY_HOST = 'api.weapp.com'
    #sevice celery 相关
    EVENT_DISPATCHER = 'local'
    ENABLE_SQL_LOG = False

    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        #filename='myapp.log',
        #filemode='w'
        )

else:
    # 真实环境暂时关闭
    #WAPI_LOGGER_ENABLED = False
    # 生产环境开启API Logger
    WAPI_LOGGER_ENABLED = True
    WAPI_LOGGER_SERVER_HOST = 'mongo.weapp.com'
    WAPI_LOGGER_SERVER_PORT = 27017
    WAPI_LOGGER_DB = 'wapi'
    IMAGE_HOST = 'http://dev.weapp.com'
    PAY_HOST = 'api.weapp.com'
    ENABLE_SQL_LOG = False

    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        #filename='apiserver.log',
        #filemode='w+'
        )


#缓存相关配置
REDIS_HOST = 'redis.weapp.com'
REDIS_PORT = 6379
REDIS_CACHES_DB = 1

#BDD相关配置
WEAPP_DIR = '../weapp'
WEAPP_BDD_SERVER_HOST = '127.0.0.1'
WEAPP_BDD_SERVER_PORT = 8170
ENABLE_BDD_DUMP_RESPONSE = True

#watchdog相关
#WATCH_DOG_DEVICE = 'mysql'
WATCH_DOG_DEVICE = 'mongo'
WATCH_DOG_LEVEL = 200
WATCHDOG_CONFIG = {
    'TYPE': 'mongo',
    'SERVER_HOST': 'mongo.weapp.com',
    'SERVER_PORT': 27017,
    'DATABASE': 'watchdog'
}


IS_UNDER_BDD = False
# 是否开启TaskQueue(基于Celery)
TASKQUEUE_ENABLED = True


# Celery for Falcon
INSTALLED_TASKS = [
    #'resource.member.tasks',
    'core.watchdog.tasks.send_watchdog',
    'apitasks',
    
    'services.example_service.tasks.example_log_service',
    'services.order_notify_mail_service.task.notify_order_mail',
    'services.record_member_pv_service.task.record_member_pv',
    'services.update_member_from_weixin.task.update_member_info',
    'services.record_order_status_log_service.task.record_order_status_log',
    'services.update_product_sale_service.task.update_product_sale',
    'services.send_template_message_service.task.send_template_message',
    'services.order_notify_mail_service.task.notify_group_buy_after_pay',
    ]

#redis celery相关
REDIS_SERVICE_DB = 2

CTYPT_INFO = {
    'id': 'weizoom_h5',
    'token': '2950d602ffb613f47d7ec17d0a802b',
    'encodingAESKey': 'BPQSp7DFZSs1lz3EBEoIGe6RVCJCFTnGim2mzJw5W4I'
}

if MODE == 'test':
    APPID = 'wx9b89fe19768a02d2'
else:
    APPID = 'wx8209f1f63f0b1d26'

COMPONENT_INFO = {
        'app_id' : APPID,
    }


PROMOTION_RESULT_VERSION = '2' #促销结果数据版本号


UPLOAD_DIR = os.path.join(PROJECT_HOME, '../static', 'upload')

# 通知用邮箱
# MAIL_NOTIFY_USERNAME = u'noreply@weizoom.com'
# MAIL_NOTIFY_PASSWORD = u'#weizoom2013'
# MAIL_NOTIFY_ACCOUNT_SMTP = u'smtp.mxhichina.com'
# MAIL_NOTIFY_USERNAME = u'972122220@qq.com'
# MAIL_NOTIFY_PASSWORD = u'irocwdrjrpkzbcfa'
# MAIL_NOTIFY_ACCOUNT_SMTP = u'smtp.qq.com'

MAIL_NOTIFY_USERNAME = u'noreply@notice.weizoom.com'
MAIL_NOTIFY_PASSWORD = u'Weizoom2015'
MAIL_NOTIFY_ACCOUNT_SMTP = u'smtp.dm.aliyun.com'


#最为oauthserver时候使用
if MODE == 'test':
    OAUTHSERVER_HOST = 'http://api.mall3.weizzz.com/'
    H5_DOMAIN = 'h5.mall3.weizzz.com'
    WEAPP_DOMAIN = 'docker.test.weizzz.com'
elif MODE == 'develop':
    OAUTHSERVER_HOST = 'http://api.weizoom.com/'
    H5_DOMAIN = 'mall.weizoom.com'
    WEAPP_DOMAIN = 'dev.weapp.com'
else:
    OAUTHSERVER_HOST = 'http://api.weizoom.com/'
    H5_DOMAIN = 'mall.weizoom.com'
    WEAPP_DOMAIN = 'weapp.weizoom.com'


DEV_SERVER_MULTITHREADING = False

REDIS_CACHE_KEY = ':1:api'